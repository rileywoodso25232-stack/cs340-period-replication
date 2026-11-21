#!/usr/bin/env python3
"""Prepare an isolated PERIOD Serial IPC candidate; optionally run one smoke test.

Python 3.6+. No network, package installation, source overwrite, or IPC deletion.
This is a compatibility experiment, not a verified paper Serial baseline.
"""
import argparse
import ast
import ctypes as C
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HELPERS = ('setup_share_memroy', 'get_info_from_share_memory', 'memmove_pattern_list')
ARRAYS = ('kpNumArray', 'kpYieldArray', 'kpLocArray', 'kpOrderArray')
# Independently decoded from the archived ELF's DWARF 4 Sched_Info DIE (offset 50609).
VERIFIED_BINARY_SHA256 = 'ed2d13809b87a00eaaba76ac0f1faf4871a489a0960993e5963dc89b4bb13db9'

CHECKED_SETUP = '''def setup_share_memroy():
    from ctypes import CDLL, get_errno, set_errno
    class CompatSchedInfo(Structure):
        _fields_ = [('time', c_uint64), ('N', c_uint32), ('M', c_uint32),
                    ('bounds', c_uint32), ('kpNumArray', c_uint16*SHARE_THREAD_NUM),
                    ('kp', c_uint16*SHARE_ARRAY_SIZE),
                    ('kpLoc', c_uint16*SHARE_ARRAY_SIZE),
                    ('kpOrder', c_uint16*SHARE_ARRAY_SIZE)]
    expected = (24008, 20, 220, 8148, 16076)
    actual = (sizeof(CompatSchedInfo), CompatSchedInfo.kpNumArray.offset,
              CompatSchedInfo.kp.offset, CompatSchedInfo.kpLoc.offset,
              CompatSchedInfo.kpOrder.offset)
    if sizeof(c_void_p) != 8 or actual != expected:
        raise RuntimeError('Unexpected candidate ABI: ' + repr(actual))
    with open('/proc/sysvipc/shm') as ipc_file:
        rows = [row.split() for row in ipc_file if row.strip()]
    segments = [dict(zip(rows[0], row)) for row in rows[1:]]
    matches = [row for row in segments if int(row['key']) == 1111]
    if len(matches) != 1 or int(matches[0]['size']) != actual[0]:
        raise RuntimeError('Expected existing key 1111 segment of size 24008')
    if int(matches[0]['nattch']) != 0:
        raise RuntimeError('Shared memory is in use; run this experiment alone')
    libc = CDLL('libc.so.6', use_errno=True)
    libc.shmget.argtypes = [c_int, c_size_t, c_int]
    libc.shmget.restype = c_int
    libc.shmat.argtypes = [c_int, c_void_p, c_int]
    libc.shmat.restype = c_void_p
    set_errno(0)
    shm_id = libc.shmget(1111, sizeof(CompatSchedInfo), 0)
    if shm_id == -1:
        err = get_errno()
        raise OSError(err, os.strerror(err))
    set_errno(0)
    address = libc.shmat(shm_id, None, 0)
    if address is None or address == c_void_p(-1).value:
        err = get_errno()
        raise OSError(err, os.strerror(err))
    print('Candidate IPC ABI: size=24008, offsets=20/220/8148/16076', flush=True)
    return address

'''


def top_functions(source):
    lines = source.splitlines(True)
    body = ast.parse(source).body
    found = {}
    for i, node in enumerate(body):
        if isinstance(node, ast.FunctionDef) and node.name in HELPERS:
            # Compatible with Python 3.6 (no AST end_lineno).
            start = node.lineno - 1
            end = body[i + 1].lineno - 1 if i + 1 < len(body) else len(lines)
            found[node.name] = (start, end, ''.join(lines[start:end]))
    if set(found) != set(HELPERS):
        raise ValueError('Expected exactly the three IPC helper functions')
    return lines, found


def protected_ast(source):
    tree = ast.parse(source)
    kept = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in HELPERS:
            continue
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in ARRAYS + ('SHARE_ARRAY_SIZE',):
                continue
        kept.append(node)
    tree.body = kept
    return ast.dump(tree, include_attributes=False)


def make_candidate(old, current):
    for source in (old, current):
        for name, expected in [('SHARE_THREAD_NUM', 100), ('SHARE_ARRAY_SIZE', 1990)]:
            matches = re.findall(r'^' + name + r'\s*=\s*(\d+)\s*$', source, re.M)
            if matches != [str(expected)]:
                raise ValueError('Unexpected source constants: ' + name)
    lines, old_helpers = top_functions(old)
    unused, new_helpers = top_functions(current)
    replacements = []
    for name in HELPERS:
        start, end, unused = old_helpers[name]
        replacement = CHECKED_SETUP if name == 'setup_share_memroy' else new_helpers[name][2]
        if name == 'memmove_pattern_list':
            marker = '    tmparr = (c_uint16 * len(tmp))(*tmp)'
            if replacement.count(marker) != 1:
                raise ValueError('Unexpected current pattern writer')
            replacement = replacement.replace(marker,
                "    if len(tmp) > SHARE_ARRAY_SIZE or any(v < 0 or v > 65535 for v in tmp):\n"
                "        raise ValueError('Pattern exceeds candidate IPC capacity')\n" + marker)
        replacements.append((start, end, replacement))
    for start, end, replacement in sorted(replacements, reverse=True):
        lines[start:end] = [replacement]
    result = ''.join(lines)
    result, count = re.subn(r'^SHARE_ARRAY_SIZE\s*=\s*1990\s*$',
                            'SHARE_ARRAY_SIZE = 3964', result, flags=re.M)
    if count != 1:
        raise ValueError('Array capacity replacement failed')
    for name in ARRAYS:
        pattern = r'(^' + name + r'\s*=\s*\()c_uint(\s*\*\s*SHARE_(?:THREAD_NUM|ARRAY_SIZE)\)\(0\))'
        result, count = re.subn(pattern, r'\1c_uint16\2', result, flags=re.M)
        if count != 1:
            raise ValueError('Unexpected array definition: ' + name)
    for field in ('kpNumArray', 'kp', 'kpLoc', 'kpOrder'):
        result = re.sub(r'(#\s*)unsigned int (' + field + r'\[)',
                        r'\1uint16_t \2', result)
    if protected_ast(old) != protected_ast(result):
        raise ValueError('Refusing a change outside IPC helpers and arrays')
    compile(result, 'run_SerialCompat_candidate.py', 'exec')
    return '# Candidate IPC compatibility experiment; paper Serial identity unverified.\n' + result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ipc_idle_preflight():
    # Check before Dry Run: the runtime itself resets the shared segment.
    with open('/proc/sysvipc/shm') as ipc_file:
        rows = [row.split() for row in ipc_file if row.strip()]
    segments = [dict(zip(rows[0], row)) for row in rows[1:]]
    matches = [row for row in segments if int(row['key']) == 1111]
    if len(matches) > 1:
        raise RuntimeError('Unexpected multiple key 1111 segments')
    if matches:
        if int(matches[0]['size']) != 24008:
            raise RuntimeError('Existing key 1111 segment is not 24008 bytes; leaving it untouched')
        if int(matches[0]['nattch']) != 0:
            raise RuntimeError('Shared memory is in use; no Dry Run was started')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--period-root', default='/workdir/PERIOD')
    parser.add_argument('--output-root', default='/workdir/cs340-runs')
    parser.add_argument('--run', action='store_true', help='Run one 120-second candidate smoke test')
    args = parser.parse_args()
    root = Path(args.period_root).resolve()
    dbds = root / 'tool/DBDS'
    old_path, current_path = dbds / 'run_OldPDS.py', dbds / 'run_PDS.py'
    old, current = old_path.read_text(encoding='utf-8'), current_path.read_text(encoding='utf-8')
    candidate = make_candidate(old, current)
    output_root = Path(args.output_root).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='serial-compat-candidate-', dir=str(output_root)))
    print('Evidence directory: ' + str(output), flush=True)
    driver = output / 'driver'
    driver.mkdir()
    for path in dbds.glob('*.py'):
        shutil.copy2(str(path), str(driver / path.name))
    runtime_path = root / 'tool/staticAnalysis/DBDS-INSTRU/llvm-mode/DBDSFunction.cpp'
    if runtime_path.is_file():
        shutil.copy2(str(runtime_path), str(output / 'runtime-source.cpp'))
        runtime = runtime_path.read_text(encoding='utf-8')
        if re.search(r'\bSHARE_MEMORY_ARRAY_SIZ\b', runtime):
            print('NOTE: runtime source contains SHARE_MEMORY_ARRAY_SIZ; source/binary provenance needs review.')
    (driver / 'run_SerialCompat_candidate.py').write_text(candidate, encoding='utf-8')
    (output / 'driver.diff').write_text(''.join(difflib.unified_diff(
        old.splitlines(True), candidate.splitlines(True),
        fromfile='original/run_OldPDS.py', tofile='candidate/run_SerialCompat_candidate.py')), encoding='utf-8')
    target = root / 'evaluation/CS/reorder_3'
    for name in ('reorder_3_bad', 'ConConfig.reorder_3_bad', 'mempair.reorder_3_bad.npz'):
        shutil.copy2(str(target / name), str(output / name))
    shutil.copy2(str(Path(__file__).resolve()), str(output / 'prepare_serial_compat.py'))
    files = [p for p in output.rglob('*') if p.is_file()]
    (output / 'hashes.sha256').write_text(''.join(
        digest(p) + '  ' + str(p.relative_to(output)) + '\n' for p in sorted(files)), encoding='utf-8')
    binary_hash = digest(output / 'reorder_3_bad')
    abi_verified = binary_hash == VERIFIED_BINARY_SHA256
    notes = {
        'kind': 'Serial IPC compatibility candidate; paper Serial baseline unverified',
        'binary_abi_status': ('Verified by exact SHA256 match to archived ELF DWARF layout'
                              if abi_verified else 'Unverified binary; --run is refused'),
        'verified_binary_sha256': VERIFIED_BINARY_SHA256,
        'dwarf_struct_die_offset': 50609,
        'thread_capacity': 100, 'array_capacity': 3964, 'array_bits': 16,
        'struct_size': 24008, 'array_offsets': [20, 220, 8148, 16076],
        'original_old_driver_sha256': digest(old_path), 'original_current_driver_sha256': digest(current_path),
        'binary_sha256': binary_hash,
        'scope': 'Original SBPSched search control flow retained; only IPC compatibility changed',
        'limit': 'Do not compare formally against old PERIOD runs made with array capacity 1990',
    }
    (output / 'manifest.json').write_text(json.dumps(notes, indent=2) + '\n', encoding='utf-8')
    command = ['timeout', '--kill-after=10s', '120s', sys.executable, '-u', '-X', 'faulthandler',
               str(driver / 'run_SerialCompat_candidate.py'), '-y', '-d', '3', '-f', '10000', '-t', '5', './reorder_3_bad']
    import shlex
    (output / 'command.txt').write_text(' '.join(shlex.quote(x) for x in command) + '\n', encoding='utf-8')
    if not args.run:
        print('Prepared only. Command saved in: ' + str(output / 'command.txt'))
        return 0
    if sys.platform != 'linux' or C.sizeof(C.c_void_p) != 8:
        raise RuntimeError('Run the smoke test inside the 64-bit Linux container')
    if not shutil.which('timeout'):
        raise RuntimeError('GNU timeout is required')
    print('Target SHA256: ' + binary_hash, flush=True)
    if not abi_verified:
        raise RuntimeError('Target differs from the DWARF-verified binary; no Dry Run was started. See manifest.json.')
    ipc_idle_preflight()
    print('Running one candidate smoke test. Run no other PERIOD/Serial experiments concurrently.', flush=True)
    import resource
    def disable_core():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    with (output / 'search.log').open('wb') as log:
        completed = subprocess.run(command, cwd=str(output), stdout=log, stderr=subprocess.STDOUT,
                                   preexec_fn=disable_core)
    (output / 'search.exit').write_text(str(completed.returncode) + '\n', encoding='ascii')
    print('Driver/timeout exit code: ' + str(completed.returncode))
    if completed.returncode in (124, 137):
        print('Outer timeout: run incomplete. Do not retry until remaining target processes/IPC usage are checked.')
    print('--- Last 80 log lines ---')
    print('\n'.join((output / 'search.log').read_text(encoding='utf-8', errors='replace').splitlines()[-80:]))
    print('Evidence directory: ' + str(output))
    print('Candidate run only; inspect logs, saved schedules, and replay before reporting findings.')
    return completed.returncode if completed.returncode >= 0 else 128 - completed.returncode


if __name__ == '__main__':
    sys.exit(main())

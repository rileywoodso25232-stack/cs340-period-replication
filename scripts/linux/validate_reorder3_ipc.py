#!/usr/bin/env python3
"""Apply archived IPC patches to isolated copies; run one search/replay per mode.

Python 3.6+. Run inside `unshare --ipc --fork`, with no other experiments in that
namespace. Keeps all evidence in a new Linux directory; never edits upstream.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path('/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069')
REPO = Path(__file__).resolve().parents[2]
TARGET_NAME = 'reorder_3_bad'
HELPERS = {'setup_share_memroy', 'get_info_from_share_memory', 'memmove_pattern_list'}
ARRAYS = {'SHARE_ARRAY_SIZE', 'kpNumArray', 'kpYieldArray', 'kpLocArray', 'kpOrderArray'}

# This observer records target exits without changing driver source or status handling.
OBSERVER = '''import json, os, runpy, subprocess, sys
original_popen = subprocess.Popen
class ObservedPopen(original_popen):
    def communicate(self, *args, **kwargs):
        try:
            return super().communicate(*args, **kwargs)
        finally:
            if self.returncode is not None and not getattr(self, '_recorded', False):
                with open(os.environ['CS340_TARGET_EXITS'], 'a', encoding='utf-8') as log:
                    log.write(json.dumps({'pid': self.pid, 'args': self.args, 'returncode': self.returncode}) + '\\n')
                self._recorded = True
subprocess.Popen = ObservedPopen
driver = sys.argv[1]
sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(driver))
runpy.run_path(driver, run_name='__main__')
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')


def protected_ast(text):
    tree = ast.parse(text)
    tree.body = [n for n in tree.body if not (
        isinstance(n, ast.FunctionDef) and n.name in HELPERS or
        isinstance(n, ast.Assign) and len(n.targets) == 1 and
        isinstance(n.targets[0], ast.Name) and n.targets[0].id in ARRAYS)]
    return ast.dump(tree, include_attributes=False)


def run(command, directory, env, label):
    save_json(directory / (label + '.command.json'), {'argv': command, 'cwd': str(directory),
              'outer_timeout_seconds': 120, 'environment': {k: env[k] for k in
              ('ROOT_DIR', 'PATH', 'LD_LIBRARY_PATH', 'LC_ALL', 'CS340_TARGET_EXITS') if k in env}})
    started = time.monotonic()
    with (directory / (label + '.log')).open('wb') as log:
        process = subprocess.Popen(command, cwd=str(directory), env=env, stdout=log,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            process.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
    result = {'driver_exit': process.returncode, 'outer_timeout': timed_out,
              'wrapper_elapsed_seconds': time.monotonic() - started}
    save_json(directory / (label + '.result.json'), result)
    if timed_out or process.returncode != 0:
        raise RuntimeError(label + ' failed; inspect ' + str(directory))
    return result


def main():
    if os.readlink('/proc/self/ns/ipc') == os.readlink('/proc/1/ns/ipc'):
        raise RuntimeError('Run with unshare --ipc --fork; refusing host IPC namespace')
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    parent = Path('/root/cs340-period/validation')
    parent.mkdir(exist_ok=True)
    output = Path(tempfile.mkdtemp(prefix='ipc-reorder3-20261115-', dir=str(parent)))
    print('Evidence directory: ' + str(output), flush=True)
    shutil.copy2(str(Path(__file__)), str(output / Path(__file__).name))
    (output / 'observe_driver.py').write_text(OBSERVER, encoding='utf-8')
    environment = os.environ.copy()
    environment.update(ROOT_DIR=str(ROOT), LC_ALL='C.UTF-8', PYTHONUNBUFFERED='1',
                       PYTHONDONTWRITEBYTECODE='1')
    environment['PATH'] = str(ROOT / 'clang+llvm/bin') + ':' + environment['PATH']
    environment['LD_LIBRARY_PATH'] = str(ROOT / 'clang+llvm/lib')
    probe = subprocess.run([sys.executable, str(REPO / 'scripts/linux/probe_deadline.py')],
                           env=environment, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output / 'deadline-probe.json').write_bytes(probe.stdout)
    (output / 'deadline-probe.stderr').write_bytes(probe.stderr)
    if probe.returncode:
        raise RuntimeError('SCHED_DEADLINE probe failed; no target started')
    source_dir = ROOT / 'tool/DBDS'
    files = list(source_dir.glob('*.py'))
    target_dir = ROOT / 'evaluation/CS/reorder_3'
    target_files = [target_dir / name for name in
                    (TARGET_NAME, 'ConConfig.' + TARGET_NAME, 'mempair.' + TARGET_NAME + '.npz')]
    originals = {str(p): digest(p) for p in files + target_files}
    dwarf = subprocess.check_output(['readelf', '--debug-dump=info', str(target_files[0])]).decode('utf-8')
    start = dwarf.index(': Sched_Info')
    excerpt = dwarf[start:start + 7000]
    (output / 'target-dwarf.txt').write_text(excerpt, encoding='utf-8')
    # Fail closed for a different ELF layout; excerpt includes array types and offsets.
    if not all(re.search(pattern, excerpt) for pattern in (
            r'DW_AT_byte_size\s*:\s*24008', r'DW_AT_count\s*:\s*3964',
            r'DW_AT_data_member_location:\s*8148', r'DW_AT_data_member_location:\s*16076')):
        raise RuntimeError('Target layout differs from the inspected ABI')
    manifest = {'kind': 'one-run candidate compatibility validation per method',
                'kernel': platform.release(), 'python': sys.version, 'cpu_affinity': sorted(os.sched_getaffinity(0)),
                'upstream_commit': 'cb8deb9a176e5bb292d70d46557dd61dc0e98069',
                'patch_repository_commit': '9287fe43e351c650e6d48311e9368062b07f07e6',
                'source_hashes_before': originals, 'ipc_namespace': os.readlink('/proc/self/ns/ipc'),
                'configuration': {'depth_argument': 3, 'schedule_budget': 10000,
                                  'child_timeout_seconds': 5, 'outer_timeout_seconds': 120,
                                  'repetitions': 1}, 'modes': {}}
    save_json(output / 'manifest.json', manifest)
    for mode, filename in [('period', 'run_PDS.py'), ('serial', 'run_OldPDS.py')]:
        mode_dir = output / mode
        driver_dir = mode_dir / 'driver'
        driver_dir.mkdir(parents=True)
        for src in files:
            shutil.copy2(str(src), str(driver_dir / src.name))
        driver = driver_dir / filename
        patch = REPO / 'src/patches/teammate-ipc-compat' / (mode + '.diff')
        patched = subprocess.run(['patch', '--batch', '--fuzz=0', str(driver)], input=patch.read_bytes(),
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (mode_dir / 'patch.log').write_bytes(patched.stdout)
        shutil.copy2(str(patch), str(mode_dir / 'applied.diff'))
        if patched.returncode or protected_ast((source_dir / filename).read_text()) != protected_ast(driver.read_text()):
            raise RuntimeError('Patch failed or changed protected search logic')
        compile(driver.read_text(), str(driver), 'exec')
        manifest['modes'][mode] = {'driver_file': filename, 'driver_sha256': digest(driver),
                                    'patch_sha256': digest(patch), 'protected_ast_unchanged': True}
        for stage in ('search', 'replay'):
            directory = mode_dir / stage
            directory.mkdir()
            for src in target_files:
                shutil.copy2(str(src), str(directory / src.name))
            env = environment.copy()
            env['CS340_TARGET_EXITS'] = str(directory / 'target-exits.jsonl')
            command = [sys.executable, '-u', str(output / 'observe_driver.py'), str(driver),
                       '-y', '-d', '3', '-f', '10000', '-t', '5']
            if stage == 'replay':
                candidates = sorted((mode_dir / 'search' / ('out_' + TARGET_NAME + '_1') / 'Errors').glob('*'))
                if not candidates:
                    raise RuntimeError('No saved failure to replay')
                failure = candidates[0]
                shutil.copy2(str(failure), str(directory / 'failure.schedule'))
                command += ['-r', 'failure.schedule']
            command += ['./' + TARGET_NAME]
            result = run(command, directory, env, stage)
            text = re.sub(r'\x1b\[[0-9;]*m', '', (directory / (stage + '.log')).read_text())
            if stage == 'search':
                if 'End Testing!' not in text or 'Candidate IPC ABI: size=24008' not in text:
                    raise RuntimeError('Search completion/ABI marker missing')
                patterns = {'schedules': r'^Round\s+\d+\s+(\d+)',
                            'error_schedules': r'Total Error Interleavings:\s*(\d+)',
                            'timeouts': r'Total Timeouts Interleavings:\s*(\d+)',
                            'first_bug_schedule': r'Errors/000001_(\d+)_'}
                for key, pattern in patterns.items():
                    match = re.search(pattern, text, re.M)
                    if not match:
                        raise RuntimeError('Missing metric: ' + key)
                    result[key] = int(match.group(1))
                errors = mode_dir / 'search' / ('out_' + TARGET_NAME + '_1') / 'Errors'
                if len(list(errors.iterdir())) != result['error_schedules'] or result['timeouts']:
                    raise RuntimeError('Saved failures/counts disagree or timeouts occurred')
            else:
                exits = [json.loads(line) for line in (directory / 'target-exits.jsonl').read_text().splitlines()]
                result['observed_child_exits'] = [entry['returncode'] for entry in exits]
                result['assertion_reproduced'] = "Assertion `0' failed" in text and 'reorder_bad.c:80' in text
                if not result['assertion_reproduced'] or not exits or exits[-1]['returncode'] != -6:
                    raise RuntimeError('Replay did not confirm the expected assertion and SIGABRT')
            save_json(directory / (stage + '.result.json'), result)
            manifest['modes'][mode][stage] = result
            save_json(output / 'manifest.json', manifest)
            print(mode + ' ' + stage + ': ' + json.dumps(result), flush=True)
    after = {name: digest(Path(name)) for name in originals}
    manifest['originals_unchanged'] = after == originals
    if not manifest['originals_unchanged']:
        raise RuntimeError('Original files changed during validation')
    manifest['status'] = 'search_and_replay_passed_both_candidates'
    save_json(output / 'manifest.json', manifest)
    hashes = {str(p.relative_to(output)): digest(p) for p in output.rglob('*') if p.is_file()}
    save_json(output / 'hashes.full.json', hashes)
    print('PASS. Evidence directory: ' + str(output), flush=True)


if __name__ == '__main__':
    main()

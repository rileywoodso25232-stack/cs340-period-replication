#!/usr/bin/env python3
"""Six isolated candidate runs. Python 3.6+, Linux container only.
Requires prepare_serial_compat.py alongside this file. No originals overwritten.
"""
import csv
import difflib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time


def period_candidate(helper, current):
    # Adapt the four declarations for the existing checked transformer.
    # Its AST protection excludes these declarations but preserves all search logic.
    intermediate = current
    for name in helper.ARRAYS:
        pattern = r'(^' + name + r'\s*=\s*\()c_uint16(\s*\*\s*SHARE_(?:THREAD_NUM|ARRAY_SIZE)\)\(0\))'
        intermediate, count = re.subn(pattern, r'\1c_uint\2', intermediate, flags=re.M)
        if count != 1:
            raise ValueError('Unexpected PERIOD declaration: ' + name)
    candidate = helper.make_candidate(intermediate, current)
    if helper.protected_ast(current) != helper.protected_ast(candidate):
        raise ValueError('PERIOD control flow changed')
    return candidate


def main():
    import resource
    helper_path = Path(__file__).resolve().with_name('prepare_serial_compat.py')
    spec = importlib.util.spec_from_file_location('compat_helper', str(helper_path))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    root = Path('/workdir/PERIOD')
    dbds = root / 'tool/DBDS'
    target = root / 'evaluation/CS/reorder_3'
    if helper.digest(target / 'reorder_3_bad') != helper.VERIFIED_BINARY_SHA256:
        raise RuntimeError('Binary differs from the DWARF-verified target; no experiment started')
    old = (dbds / 'run_OldPDS.py').read_text(encoding='utf-8')
    current = (dbds / 'run_PDS.py').read_text(encoding='utf-8')
    candidates = {'serial': helper.make_candidate(old, current),
                  'period': period_candidate(helper, current)}
    output = Path(tempfile.mkdtemp(prefix='reorder3-compat-comparison-', dir='/workdir/cs340-runs'))
    print('Evidence directory: ' + str(output), flush=True)
    shutil.copy2(str(helper_path), str(output / helper_path.name))
    shutil.copy2(str(Path(__file__).resolve()), str(output / Path(__file__).name))
    notes = {
        'scope': 'Candidate driver comparison on one benchmark; paper baseline correspondence unverified',
        'binary_sha256': helper.VERIFIED_BINARY_SHA256,
        'abi': {'threads': 100, 'array_capacity': 3964, 'array_bits': 16, 'size': 24008},
        'parameters': {'depth_argument': 3, 'runs_budget': 10000, 'child_timeout_seconds': 5,
                       'outer_timeout_seconds': 120, 'repetitions': 3},
        'period_ranges_for_three_threads': {'serial': [3, 4, 5], 'period': [2, 3, 4]},
        'timing_limit': 'Drivers retain different runtime amplification and initialization logic. No speedup claim.',
        'old_results': 'Old 1990-capacity runs remain historical pre-experiments; not replaced or pooled.',
        'ordering': 'serial/period alternated, one process at a time',
    }
    (output / 'manifest.json').write_text(json.dumps(notes, indent=2) + '\n', encoding='utf-8')
    for method in ('serial', 'period'):
        driver = output / method / 'driver'
        driver.mkdir(parents=True)
        for path in dbds.glob('*.py'):
            shutil.copy2(str(path), str(driver / path.name))
        (driver / 'run_candidate.py').write_text(candidates[method], encoding='utf-8')
        original = old if method == 'serial' else current
        (driver.parent / 'driver.diff').write_text(''.join(difflib.unified_diff(
            original.splitlines(True), candidates[method].splitlines(True),
            fromfile='original', tofile=method + '-candidate')), encoding='utf-8')
    records = []
    def no_core():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    for repeat in range(1, 4):
        for method in ('serial', 'period'):
            helper.ipc_idle_preflight()
            group = output / method / ('group-' + str(repeat))
            group.mkdir()
            for name in ('reorder_3_bad', 'ConConfig.reorder_3_bad', 'mempair.reorder_3_bad.npz'):
                shutil.copy2(str(target / name), str(group / name))
            command = ['timeout', '--kill-after=10s', '120s', sys.executable, '-u', '-X', 'faulthandler',
                       str(output / method / 'driver/run_candidate.py'), '-y', '-d', '3', '-f', '10000', '-t', '5', './reorder_3_bad']
            (group / 'command.json').write_text(json.dumps(command, indent=2) + '\n', encoding='utf-8')
            print('Running {} group {}'.format(method, repeat), flush=True)
            start = time.monotonic()
            with (group / 'search.log').open('wb') as log:
                process = subprocess.run(command, cwd=str(group), stdout=log,
                                         stderr=subprocess.STDOUT, preexec_fn=no_core)
            elapsed = time.monotonic() - start
            (group / 'search.exit').write_text(str(process.returncode) + '\n', encoding='ascii')
            text = (group / 'search.log').read_text(encoding='utf-8', errors='replace')
            rounds = re.findall(r'^test\s+(\d+):', text, re.M)
            errors = re.findall(r'Total Error Interleavings:\s*(\d+)', text)
            timeouts = re.findall(r'Total Timeouts Interleavings:\s*(\d+)', text)
            complete = process.returncode == 0 and 'End Testing!' in text and bool(errors) and bool(timeouts)
            record = {'method': method, 'group': repeat, 'exit': process.returncode,
                      'complete': complete, 'schedules': len(rounds),
                      'error_schedules': int(errors[-1]) if errors else '',
                      'timeouts': int(timeouts[-1]) if timeouts else '',
                      'wrapper_elapsed_seconds': round(elapsed, 6)}
            records.append(record)
            with (output / 'summary.csv').open('w', newline='', encoding='utf-8') as report:
                writer = csv.DictWriter(report, fieldnames=list(record))
                writer.writeheader()
                writer.writerows(records)
            print(json.dumps(record), flush=True)
            if not complete:
                print('\n'.join(text.splitlines()[-60:]))
                print('Incomplete run: stopped without retry. Evidence: ' + str(output))
                return 1
    files = [p for p in output.rglob('*') if p.is_file()]
    (output / 'hashes.sha256').write_text(''.join(helper.digest(p) + '  ' + str(p.relative_to(output)) + '\n'
        for p in sorted(files)), encoding='utf-8')
    print('Six runs finished. Evidence directory: ' + str(output))
    print('Saved failures need replay; counts are schedules, not distinct bugs.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Controlled check: does replaying a 15265 failure in the search IPC namespace
reproduce the bug more often than replaying it in a fresh namespace?

Each trial runs one search, then replays that search's first saved failure twice:
once in the same IPC namespace/state as the search, once in a fresh namespace.
Everything else (driver, target, depth, budget, timeouts, machine) is held fixed.
"""
import argparse
import csv
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from run_table1_pilot import digest, environment, parse_search, save

SUBJECT = 'CVE-2017-15265'
BINARY = '2017-15265'
EXPECTED = 'heap-use-after-free'
DEPTH = 5
BUDGET = 10000
CHILD_TIMEOUT = 5
OUTER_TIMEOUT = 120


def run_shell(command, cwd, env, log_path, timeout):
    started = time.monotonic()
    with Path(log_path).open('wb') as handle:
        child = subprocess.Popen(command, cwd=str(cwd), env=env, stdout=handle,
                                 stderr=subprocess.STDOUT, start_new_session=True)
        timed_out = False
        try:
            child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
    return {'exit_code': child.returncode, 'outer_timeout': timed_out,
            'elapsed_seconds': time.monotonic() - started}


def read_exits(path):
    if not Path(path).is_file():
        return []
    return [json.loads(line)['returncode'] for line in
            Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def classify_replay(text, exits):
    reproduction = 'Perform Reproduction!' in text
    asan = 'AddressSanitizer' in text
    expected = EXPECTED in text
    binary = BINARY in text
    last = exits[-1] if exits else None
    confirmed = reproduction and asan and expected and binary and last in (1, -6)
    if confirmed:
        status = 'confirmed'
    elif (not reproduction) and 'Perform Dry Run!' in text and asan:
        status = 'dry_run_asan_abort'
    elif reproduction:
        status = 'ran_without_expected_diagnostic'
    else:
        status = 'other_error'
    return {'status': status, 'reproduction_started': reproduction, 'asan_reported': asan,
            'expected_diagnostic': expected, 'last_child_exit': last}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot-dir', required=True)
    parser.add_argument('--trials', type=int, default=5)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()

    pilot = Path(args.pilot_dir).resolve()
    manifest = json.loads((pilot / 'manifest.json').read_text(encoding='utf-8'))
    build = pilot / 'build' / SUBJECT
    expected_hashes = manifest['targets'][SUBJECT]
    for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY, 'mempair.' + BINARY + '.npz']:
        if digest(build / name) != expected_hashes[name]:
            raise SystemExit('Target changed: ' + name)
    driver = pilot / 'driver-period/run_PDS.py'
    if digest(driver) != manifest['methods']['period']['driver_sha256']:
        raise SystemExit('Driver changed')
    observer = pilot / 'observe_driver.py'

    base = Path('/root/cs340-period/controlled')
    base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='15265-namespace-', dir=str(base)))
    destination = Path(args.destination).resolve()
    if destination.exists():
        raise SystemExit('Destination already exists: ' + str(destination))
    env = environment()

    rows = []
    for trial_number in range(1, args.trials + 1):
        trial = work / ('trial-%02d' % trial_number)
        search_dir = trial / 'search'
        same = trial / 'same-namespace-replay'
        fresh = trial / 'fresh-namespace-replay'
        for directory in (search_dir, same, fresh):
            directory.mkdir(parents=True)
        for directory in (search_dir, same, fresh):
            for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY,
                         'mempair.' + BINARY + '.npz']:
                shutil.copy2(str(build / name), str(directory / name))

        shell_script = r'''
set -u
cd "{search}"
export CS340_TARGET_EXITS="{search}/target-exits.jsonl"
python3 -u "{observer}" "{driver}" -y -d {depth} -f {budget} -t {child} "./{binary}" > "{search}/search.log" 2>&1
status=$?
echo "search_rc=$status" > "{trial}/search.rc"
if ls "{search}"/out_{binary}_1/Errors/* >/dev/null 2>&1; then
  first=$(ls "{search}"/out_{binary}_1/Errors/* | head -1)
  cp "$first" "{same}/failure.schedule"
  cd "{same}"
  export CS340_TARGET_EXITS="{same}/target-exits.jsonl"
  python3 -u "{observer}" "{driver}" -y -d {depth} -f {budget} -t {child} -r failure.schedule "./{binary}" \
      > "{same}/replay.log" 2>&1
  echo "same_rc=$?" > "{trial}/same.rc"
else
  echo "no_failure" > "{trial}/same.rc"
fi
'''.format(search=str(search_dir), same=str(same), trial=str(trial), observer=str(observer),
           driver=str(driver), depth=DEPTH, budget=BUDGET, child=CHILD_TIMEOUT, binary=BINARY)
        same_result = run_shell(['unshare', '--ipc', '--fork', 'bash', '-c', shell_script],
                                trial, env, trial / 'same-namespace.log', OUTER_TIMEOUT)
        search_log = search_dir / 'search.log'
        search_text = re.sub(r'\x1b\[[0-9;]*m', '',
                             search_log.read_text(encoding='utf-8', errors='replace')) if search_log.is_file() else ''
        search_status = 'no_search_log'
        search_result = {}
        if 'End Testing!' in search_text and 'Perform DBDS Run' in search_text:
            errors = sorted((search_dir / ('out_' + BINARY + '_1') / 'Errors').glob('*'))
            parsed, issue = parse_search(search_text, errors)
            search_result = parsed
            search_status = 'completed' if not issue else 'incomplete:' + str(issue)
        elif 'AddressSanitizer' in search_text and 'Perform DBDS Run' not in search_text:
            search_status = 'dry_run_asan_abort'

        same_status = 'not_run'
        same_exit = None
        same_log = same / 'replay.log'
        if same_log.is_file():
            same_text = re.sub(r'\x1b\[[0-9;]*m', '',
                               same_log.read_text(encoding='utf-8', errors='replace'))
            same_exits = read_exits(same / 'target-exits.jsonl')
            same_result_details = classify_replay(same_text, same_exits)
            same_status = same_result_details['status']
            same_exit = same_result_details['last_child_exit']

        fresh_status = 'not_run'
        fresh_exit = None
        if (same / 'failure.schedule').is_file():
            shutil.copy2(str(same / 'failure.schedule'), str(fresh / 'failure.schedule'))
            fresh_env = dict(env)
            fresh_env['CS340_TARGET_EXITS'] = str(fresh / 'target-exits.jsonl')
            command = ['unshare', '--ipc', '--fork', sys.executable, '-u', str(observer),
                       str(driver), '-y', '-d', str(DEPTH), '-f', str(BUDGET),
                       '-t', str(CHILD_TIMEOUT), '-r', 'failure.schedule', './' + BINARY]
            run_shell(command, fresh, fresh_env, fresh / 'replay.log', OUTER_TIMEOUT)
            fresh_text = re.sub(r'\x1b\[[0-9;]*m', '',
                                (fresh / 'replay.log').read_text(encoding='utf-8', errors='replace'))
            fresh_exits = read_exits(fresh / 'target-exits.jsonl')
            fresh_details = classify_replay(fresh_text, fresh_exits)
            fresh_status = fresh_details['status']
            fresh_exit = fresh_details['last_child_exit']

        rows.append({
            'trial': trial_number, 'search_status': search_status,
            'schedules': search_result.get('schedules', ''),
            'error_schedules': search_result.get('error_schedules', ''),
            'first_bug_schedule': search_result.get('first_bug_schedule', ''),
            'same_namespace_status': same_status, 'same_namespace_exit': same_exit if same_exit is not None else '',
            'fresh_namespace_status': fresh_status, 'fresh_namespace_exit': fresh_exit if fresh_exit is not None else '',
        })
        print('trial %02d: search=%s same=%s fresh=%s' % (
            trial_number, search_status, same_status, fresh_status), flush=True)

    columns = ['trial', 'search_status', 'schedules', 'error_schedules', 'first_bug_schedule',
               'same_namespace_status', 'same_namespace_exit', 'fresh_namespace_status',
               'fresh_namespace_exit']
    with (work / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    comparable = [r for r in rows if r['same_namespace_status'] != 'not_run'
                  and r['fresh_namespace_status'] != 'not_run']
    save(work / 'aggregate.json', {
        'trials': len(rows), 'comparable_trials': len(comparable),
        'same_namespace_confirmed': sum(1 for r in comparable
                                        if r['same_namespace_status'] == 'confirmed'),
        'fresh_namespace_confirmed': sum(1 for r in comparable
                                         if r['fresh_namespace_status'] == 'confirmed'),
        'same_namespace_statuses': [r['same_namespace_status'] for r in comparable],
        'fresh_namespace_statuses': [r['fresh_namespace_status'] for r in comparable],
        'changed_factor': 'same IPC namespace/state after search vs fresh namespace',
    })

    destination.mkdir(parents=True)
    copied, excluded = {}, {}
    for path in sorted(work.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(work)
        if path.open('rb').read(4) == b'\x7fELF' or path.stat().st_size > 2 * 1024 * 1024:
            excluded[str(relative)] = digest(path)
            continue
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(path), str(target))
        if digest(target) != digest(path):
            raise SystemExit('Copy checksum mismatch: ' + str(relative))
        copied[str(relative)] = digest(path)
    save(destination / 'packaging.json', {
        'source_directory': str(work), 'copied_files_sha256': copied,
        'excluded_files_sha256': excluded, 'all_copied_bytes_verified': True,
        'note': 'Controlled namespace/state check; formal batch untouched.',
    })
    print('Exported %d files to %s' % (len(copied), destination))
    print('Comparable trials: %d; same-ns confirmed %d; fresh-ns confirmed %d' % (
        len(comparable), sum(1 for r in comparable if r['same_namespace_status'] == 'confirmed'),
        sum(1 for r in comparable if r['fresh_namespace_status'] == 'confirmed')))


if __name__ == '__main__':
    main()

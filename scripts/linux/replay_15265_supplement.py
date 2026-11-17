#!/usr/bin/env python3
"""Bounded supplementary replay of one saved CVE-2017-15265 schedule (3.6+).

Uses the exact driver/target binary of a finished pilot run. Each replay attempt
gets a fresh directory and IPC namespace; every attempt (including dry-run
aborts) is preserved and exported with hashes.
"""
import argparse
import csv
import hashlib
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

SUBJECT = 'CVE-2017-15265'
BINARY = '2017-15265'
EXPECTED = 'heap-use-after-free'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def environment(root, exits):
    env = os.environ.copy()
    env.update(ROOT_DIR=str(root), LC_ALL='C.UTF-8', PYTHONUNBUFFERED='1',
               PYTHONDONTWRITEBYTECODE='1', CS340_TARGET_EXITS=str(exits))
    env['PATH'] = ':'.join([str(root / 'clang+llvm/bin'), str(root / 'tool/SVF/Release-build/bin'),
                            env.get('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')])
    env['LD_LIBRARY_PATH'] = str(root / 'clang+llvm/lib')
    return env


def classify(text, exits):
    result = {
        'reproduction_started': 'Perform Reproduction!' in text,
        'dry_run_started': 'Perform Dry Run!' in text,
        'asan_reported': 'AddressSanitizer' in text,
        'expected_diagnostic': EXPECTED in text,
        'binary_in_report': BINARY in text,
        'observed_child_exits': exits,
        'last_child_exit': exits[-1] if exits else None,
    }
    result['exit_ok'] = result['last_child_exit'] in (1, -6)
    confirmed = (result['reproduction_started'] and result['asan_reported']
                 and result['expected_diagnostic'] and result['binary_in_report']
                 and result['exit_ok'])
    result['confirmed'] = confirmed
    if confirmed:
        result['status'] = 'confirmed'
    elif (not result['reproduction_started'] and result['dry_run_started']
          and result['asan_reported']):
        result['status'] = 'dry_run_asan_abort'
    elif result['reproduction_started']:
        result['status'] = 'reproduction_without_expected_diagnostic'
    else:
        result['status'] = 'other_error'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot-dir', required=True)
    parser.add_argument('--run-dir', required=True,
                        help='pilot run directory, e.g. runs/CVE-2017-15265/run-3')
    parser.add_argument('--max-attempts', type=int, default=3)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--destination', required=True)
    opts = parser.parse_args()

    pilot = Path(opts.pilot_dir).resolve()
    run_dir = (pilot / opts.run_dir).resolve()
    manifest = json.loads((pilot / 'manifest.json').read_text(encoding='utf-8'))
    build = pilot / 'build' / SUBJECT
    expected_hashes = manifest['targets'][SUBJECT]
    for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY, 'mempair.' + BINARY + '.npz']:
        if digest(build / name) != expected_hashes[name]:
            raise SystemExit('Prepared target changed: ' + name)
    driver = pilot / 'driver/run_PDS.py'
    if digest(driver) != manifest['driver_sha256']:
        raise SystemExit('Prepared driver changed')

    search_result = json.loads((run_dir / 'search/search.result.json').read_text(encoding='utf-8'))
    if search_result.get('status') is None and not search_result.get('schedules'):
        raise SystemExit('Source search has no completed metrics')
    errors_dir = run_dir / ('search/out_' + BINARY + '_1/Errors')
    errors = sorted(errors_dir.glob('*'))
    if not errors:
        raise SystemExit('No saved failure schedule in ' + str(run_dir))
    schedule = errors[0]
    print('Source schedule: ' + str(schedule), flush=True)

    destination = Path(opts.destination).resolve()
    if destination.exists():
        raise SystemExit('Destination exists: ' + str(destination))
    work = Path(tempfile.mkdtemp(prefix='15265-replay-', dir='/root/cs340-period/pilots'))
    print('Replay directory: ' + str(work), flush=True)
    save(work / 'replay_manifest.json', {
        'subject': SUBJECT, 'pilot_dir': str(pilot), 'run_dir': str(run_dir),
        'source_schedule': str(schedule), 'source_schedule_sha256': digest(schedule),
        'source_search_result': search_result,
        'driver_sha256': digest(driver), 'target_sha256': digest(build / BINARY),
        'max_attempts': opts.max_attempts, 'started_utc': datetime.now(timezone.utc).isoformat(),
        'kernel': os.uname().release, 'cpu_affinity': sorted(os.sched_getaffinity(0)),
        'rule': 'bounded supplementary verification; not a new search sample; all attempts kept',
    })

    rows = []
    confirmed_attempt = None
    for index in range(1, opts.max_attempts + 1):
        attempt = work / ('replay-%02d' % index)
        attempt.mkdir(parents=True)
        for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY,
                     'mempair.' + BINARY + '.npz']:
            shutil.copy2(str(build / name), str(attempt / name))
        shutil.copy2(str(schedule), str(attempt / 'failure.schedule'))
        exits_path = attempt / 'target-exits.jsonl'
        command = ['unshare', '--ipc', '--fork', sys.executable, '-u',
                   str(pilot / 'observe_driver.py'), str(driver), '-y', '-d', '5',
                   '-f', '10000', '-t', '5', '-r', 'failure.schedule', './' + BINARY]
        save(attempt / 'replay.command.json', {
            'argv': command, 'cwd': str(attempt), 'timeout_seconds': opts.timeout,
            'start_utc': datetime.now(timezone.utc).isoformat(),
        })
        started = time.monotonic()
        with (attempt / 'replay.log').open('wb') as handle:
            child = subprocess.Popen(command, cwd=str(attempt),
                                     env=environment(Path('/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069'),
                                                     exits_path),
                                     stdout=handle, stderr=subprocess.STDOUT, start_new_session=True)
            timed_out = False
            try:
                child.communicate(timeout=opts.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(child.pid, signal.SIGKILL)
                child.communicate()
        exits = []
        if exits_path.is_file():
            exits = [json.loads(line)['returncode'] for line in
                     exits_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        text = re.sub(r'\x1b\[[0-9;]*m', '',
                      (attempt / 'replay.log').read_text(encoding='utf-8', errors='replace'))
        result = classify(text, exits)
        result.update({'attempt': index, 'exit_code': child.returncode,
                       'outer_timeout': timed_out,
                       'wrapper_elapsed_seconds': time.monotonic() - started,
                       'end_utc': datetime.now(timezone.utc).isoformat()})
        if timed_out:
            result['status'] = 'outer_timeout'
        save(attempt / 'replay.result.json', result)
        rows.append({'attempt': index, 'status': result['status'],
                     'reproduction_started': result['reproduction_started'],
                     'asan_reported': result['asan_reported'],
                     'expected_diagnostic': result['expected_diagnostic'],
                     'replay_child_exit': result['last_child_exit'],
                     'wrapper_elapsed_seconds': result['wrapper_elapsed_seconds']})
        print('replay-%02d: %s (reproduction=%s asan=%s expected=%s exit=%s)' % (
            index, result['status'], result['reproduction_started'],
            result['asan_reported'], result['expected_diagnostic'],
            result['last_child_exit']), flush=True)
        if result['status'] == 'confirmed':
            confirmed_attempt = index
            break

    columns = ['attempt', 'status', 'reproduction_started', 'asan_reported',
               'expected_diagnostic', 'replay_child_exit', 'wrapper_elapsed_seconds']
    with (work / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    aggregate = {'attempts': len(rows), 'confirmed_attempt': confirmed_attempt,
                 'confirmed': confirmed_attempt is not None,
                 'statuses': [row['status'] for row in rows]}
    save(work / 'aggregate.json', aggregate)

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
        'work_directory': str(work), 'copied_files_sha256': copied,
        'excluded_files_sha256': excluded, 'all_copied_bytes_verified': True,
        'note': 'Supplementary replay only; original pilot manifest and evidence are unchanged.',
    })
    print('Exported %d files to %s' % (len(copied), destination))
    print('CONFIRMED=%s CONFIRMED_ATTEMPT=%s ATTEMPTS=%d' % (
        aggregate['confirmed'], confirmed_attempt, len(rows)))


if __name__ == '__main__':
    main()

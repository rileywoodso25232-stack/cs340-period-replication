#!/usr/bin/env python3
"""Diagnose dry-run stability of CVE-2017-15265 with a frozen pilot build (3.6+).

Runs N minimal-budget probes (dry run plus at most one schedule) and N full
searches with the exact driver and target binary of a prepared pilot directory.
Every attempt is isolated in its own IPC namespace and output directory.
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

REPO = Path(__file__).resolve().parents[2]
SUBJECT = 'CVE-2017-15265'
BINARY = '2017-15265'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def environment(root):
    env = os.environ.copy()
    env.update(ROOT_DIR=str(root), LC_ALL='C.UTF-8', PYTHONUNBUFFERED='1',
               PYTHONDONTWRITEBYTECODE='1')
    env['PATH'] = ':'.join([str(root / 'clang+llvm/bin'), str(root / 'tool/SVF/Release-build/bin'),
                            env.get('PATH', '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')])
    env['LD_LIBRARY_PATH'] = str(root / 'clang+llvm/lib')
    return env


def run_once(attempt_dir, args, env, timeout):
    attempt_dir.mkdir(parents=True, exist_ok=True)
    command = ['unshare', '--ipc', '--fork', sys.executable, '-u', args['observer'],
               args['driver'], '-y', '-d', str(args['depth']), '-f', str(args['budget']),
               '-t', str(args['child_timeout']), './' + BINARY]
    log = attempt_dir / 'search.log'
    env = dict(env)
    env['CS340_TARGET_EXITS'] = str(attempt_dir / 'target-exits.jsonl')
    save(attempt_dir / 'search.command.json', {
        'argv': command, 'cwd': str(attempt_dir), 'timeout_seconds': timeout,
        'budget': args['budget'], 'start_utc': datetime.now(timezone.utc).isoformat(),
    })
    started = time.monotonic()
    with log.open('wb') as handle:
        child = subprocess.Popen(command, cwd=str(attempt_dir), env=env,
                                 stdout=handle, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        timed_out = False
        try:
            child.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            child.communicate()
    result = {'exit_code': child.returncode, 'outer_timeout': timed_out,
              'wrapper_elapsed_seconds': time.monotonic() - started,
              'end_utc': datetime.now(timezone.utc).isoformat()}
    text = re.sub(r'\x1b\[[0-9;]*m', '', log.read_text(encoding='utf-8', errors='replace'))
    result['dry_run_started'] = 'Perform Dry Run!' in text
    result['dbds_started'] = 'Perform DBDS Run' in text
    result['completed'] = 'End Testing!' in text
    result['asan_reported'] = 'AddressSanitizer' in text
    if text and 'Candidate IPC ABI' in text:
        abi = re.search(r'Candidate IPC ABI: size=(\d+), offsets=([0-9/]+)', text)
        result['candidate_abi'] = abi.group(0) if abi else ''
    if result['completed']:
        patterns = [('schedules', r'^Round\s+\d+\s+(\d+)'),
                    ('error_schedules', r'Total Error Interleavings:\s*(\d+)'),
                    ('timeouts', r'Total Timeouts Interleavings:\s*(\d+)'),
                    ('first_bug_schedule', r'Errors/000001_(\d+)_')]
        for key, pattern in patterns:
            match = re.search(pattern, text, re.M)
            if match:
                result[key] = int(match.group(1))
        match = re.search(r'^Time\s+\S+\s+(\d+):(\d+):([\d.]+)', text, re.M)
        if match:
            h, m, s = match.groups()
            result['tool_elapsed_seconds'] = 3600 * int(h) + 60 * int(m) + float(s)
    if result['outer_timeout']:
        result['status'] = 'outer_timeout'
    elif result['completed']:
        result['status'] = 'completed'
    elif result['asan_reported'] and not result['dbds_started']:
        result['status'] = 'dry_run_asan_abort'
    elif result['dry_run_started'] and not result['dbds_started']:
        result['status'] = 'dry_run_abort_other'
    elif result['dbds_started'] and not result['completed']:
        result['status'] = 'search_abort'
    else:
        result['status'] = 'other_error'
    save(attempt_dir / 'search.result.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot-dir', required=True,
                        help='prepared pilot directory containing build/, driver/, observer')
    parser.add_argument('--dry-runs', type=int, default=10)
    parser.add_argument('--full-runs', type=int, default=10)
    parser.add_argument('--depth', type=int, default=5)
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--small-budget', type=int, default=1)
    parser.add_argument('--child-timeout', type=int, default=5)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--destination', required=True)
    opts = parser.parse_args()

    pilot = Path(opts.pilot_dir).resolve()
    manifest = json.loads((pilot / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') not in ('prepared', 'pilot_completed', 'stopped_for_inspection'):
        raise SystemExit('Pilot directory is not usable: ' + str(manifest.get('status')))
    source_root = Path('/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069')
    if not source_root.is_dir():
        raise SystemExit('Missing source root: ' + str(source_root))
    build = pilot / 'build' / SUBJECT
    target = build / BINARY
    expected = manifest['targets'][SUBJECT]
    for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY, 'mempair.' + BINARY + '.npz']:
        if digest(build / name) != expected[name]:
            raise SystemExit('Prepared target changed: ' + name)
    driver = pilot / 'driver/run_PDS.py'
    if digest(driver) != manifest['driver_sha256']:
        raise SystemExit('Prepared driver changed')

    destination = Path(opts.destination).resolve()
    if destination.exists():
        raise SystemExit('Destination exists: ' + str(destination))
    work = Path(tempfile.mkdtemp(prefix='15265-diagnostic-', dir='/root/cs340-period/pilots'))
    print('Diagnostic directory: ' + str(work), flush=True)
    save(work / 'diagnostic.json', {
        'subject': SUBJECT, 'pilot_dir': str(pilot),
        'pilot_status': manifest.get('status'),
        'driver_sha256': digest(driver), 'target_sha256': digest(target),
        'target_hashes': expected, 'depth': opts.depth, 'budget': opts.budget,
        'small_budget': opts.small_budget, 'dry_runs': opts.dry_runs,
        'full_runs': opts.full_runs, 'child_timeout': opts.child_timeout,
        'outer_timeout': opts.timeout, 'started_utc': datetime.now(timezone.utc).isoformat(),
        'kernel': os.uname().release, 'cpu_affinity': sorted(os.sched_getaffinity(0)),
    })
    env = environment(source_root)
    args = {'observer': str(pilot / 'observe_driver.py'), 'driver': str(driver),
            'depth': opts.depth, 'child_timeout': opts.child_timeout}

    rows = []
    for phase, count, budget in [('dry', opts.dry_runs, opts.small_budget),
                                 ('full', opts.full_runs, opts.budget)]:
        for index in range(1, count + 1):
            attempt = work / ('%s-%02d' % (phase, index))
            attempt.mkdir()
            for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY,
                         'mempair.' + BINARY + '.npz']:
                shutil.copy2(str(build / name), str(attempt / name))
            run_args = dict(args)
            run_args['budget'] = budget
            result = run_once(attempt, run_args, env, opts.timeout)
            rows.append({'phase': phase, 'run': index, 'budget': budget,
                         'status': result['status'],
                         'schedules': result.get('schedules', ''),
                         'error_schedules': result.get('error_schedules', ''),
                         'timeouts': result.get('timeouts', ''),
                         'first_bug_schedule': result.get('first_bug_schedule', ''),
                         'tool_elapsed_seconds': result.get('tool_elapsed_seconds', ''),
                         'wrapper_elapsed_seconds': result['wrapper_elapsed_seconds'],
                         'exit_code': result['exit_code']})
            print('%s-%02d: %s schedules=%s first=%s' % (
                phase, index, result['status'], result.get('schedules', ''),
                result.get('first_bug_schedule', '')), flush=True)

    columns = ['phase', 'run', 'budget', 'status', 'schedules', 'error_schedules',
               'timeouts', 'first_bug_schedule', 'tool_elapsed_seconds',
               'wrapper_elapsed_seconds', 'exit_code']
    with (work / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    dry_aborts = sum(1 for r in rows if r['phase'] == 'dry'
                     and r['status'] == 'dry_run_asan_abort')
    full_completed = [r for r in rows if r['phase'] == 'full' and r['status'] == 'completed']
    full_aborts = sum(1 for r in rows if r['phase'] == 'full'
                      and r['status'] == 'dry_run_asan_abort')
    aggregate = {
        'dry_run_asan_aborts': dry_aborts,
        'dry_run_total': opts.dry_runs,
        'full_completed': len(full_completed),
        'full_total': opts.full_runs,
        'full_dry_run_asan_aborts': full_aborts,
        'full_first_bug_values': [r['first_bug_schedule'] for r in full_completed],
        'full_schedule_values': [r['schedules'] for r in full_completed],
        'full_error_values': [r['error_schedules'] for r in full_completed],
    }
    for key, field in [('full_first_bug', 'first_bug_schedule'),
                       ('full_schedules', 'schedules'),
                       ('full_errors', 'error_schedules')]:
        values = [float(r[field]) for r in full_completed if r[field] != '']
        if values:
            mean = sum(values) / len(values)
            aggregate[key + '_mean'] = mean
            if len(values) > 1:
                variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
                aggregate[key + '_sd'] = variance ** 0.5
    save(work / 'aggregate.json', aggregate)
    diagnostic = json.loads((work / 'diagnostic.json').read_text(encoding='utf-8'))
    diagnostic['ended_utc'] = datetime.now(timezone.utc).isoformat()
    diagnostic['aggregate'] = aggregate
    save(work / 'diagnostic.json', diagnostic)

    # --- export small evidence -------------------------------------------------
    destination.mkdir(parents=True)
    copied, excluded = {}, {}
    for path in sorted(work.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(work)
        if path.open('rb').read(4) == b'\x7fELF' or path.stat().st_size > 2 * 1024 * 1024:
            excluded[str(relative)] = digest(path)
            continue
        target_path = destination / relative
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(path), str(target_path))
        if digest(target_path) != digest(path):
            raise SystemExit('Copy checksum mismatch: ' + str(relative))
        copied[str(relative)] = digest(path)
    save(destination / 'packaging.json', {
        'work_directory': str(work), 'copied_files_sha256': copied,
        'excluded_files_sha256': excluded, 'all_copied_bytes_verified': True,
        'note': 'Diagnostic only; no change to the reviewed pilot configuration.',
    })
    print('Exported %d files to %s' % (len(copied), destination))
    print('DRY_ABORTS=%d/%d FULL_COMPLETED=%d/%d FULL_DRY_ABORTS=%d' % (
        dry_aborts, opts.dry_runs, len(full_completed), opts.full_runs, full_aborts))
    print('FULL_FIRST=%s FULL_SCHEDULES=%s FULL_ERRORS=%s' % (
        aggregate['full_first_bug_values'], aggregate['full_schedule_values'],
        aggregate['full_error_values']))


if __name__ == '__main__':
    main()

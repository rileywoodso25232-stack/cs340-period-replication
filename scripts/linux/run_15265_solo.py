#!/usr/bin/env python3
"""Controlled check: run CVE-2017-15265 alone, 10 attempts, same frozen setup.

Changed factor relative to the formal scoped batch: no interleaving with other
subjects. Driver, target, depth, budget, timeouts, replay policy and machine are
unchanged. Evidence is exported separately.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from run_table1_pilot import digest, save
from run_table1_formal import replay_attempt, search_attempt

SUBJECT = 'CVE-2017-15265'
BINARY = '2017-15265'
CONFIG = {
    'depth': 5,
    'schedule_budget': 10000,
    'child_timeout_seconds': 5,
    'outer_timeout_seconds': 120,
    'replay_attempts': 3,
}


def export(source, destination):
    destination.mkdir(parents=True)
    copied, excluded = {}, {}
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
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
        'source_directory': str(source), 'copied_files_sha256': copied,
        'excluded_files_sha256': excluded, 'all_copied_bytes_verified': True,
        'note': 'Controlled solo-repetition check; formal batch untouched.',
    })
    print('Exported %d files to %s' % (len(copied), destination))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot-dir', required=True)
    parser.add_argument('--attempts', type=int, default=10)
    parser.add_argument('--destination', required=True)
    args = parser.parse_args()

    pilot = Path(args.pilot_dir).resolve()
    manifest = json.loads((pilot / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('status') not in ('prepared', 'formal_completed', 'stopped_for_inspection'):
        raise SystemExit('Pilot directory is not usable')
    build = pilot / 'build' / SUBJECT
    expected = manifest['targets'][SUBJECT]
    for name in [BINARY, BINARY + '.cpp', 'ConConfig.' + BINARY, 'mempair.' + BINARY + '.npz']:
        if digest(build / name) != expected[name]:
            raise SystemExit('Target changed: ' + name)
    driver = pilot / 'driver-period/run_PDS.py'
    if digest(driver) != manifest['methods']['period']['driver_sha256']:
        raise SystemExit('Driver changed')

    base = Path('/root/cs340-period/controlled')
    base.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix='15265-solo-', dir=str(base)))
    destination = Path(args.destination).resolve()
    if destination.exists():
        raise SystemExit('Destination already exists: ' + str(destination))
    save(work / 'setup.json', {
        'experiment_id': 'local-table1-15265-solo-20261118',
        'subject': SUBJECT, 'attempts': args.attempts, 'changed_factor': 'no interleaving',
        'config': CONFIG, 'driver_sha256': digest(driver),
        'target_sha256': digest(build / BINARY),
        'started_utc': datetime.now(timezone.utc).isoformat(),
    })
    rows = []
    for number in range(1, args.attempts + 1):
        attempt = work / ('run-%02d' % number)
        attempt.mkdir(parents=True)
        search = search_attempt(attempt, pilot, CONFIG, SUBJECT, BINARY, build, driver)
        record = {'attempt': number, 'status': 'started', 'schedules': search.get('schedules', ''),
                  'error_schedules': search.get('error_schedules', ''),
                  'first_bug_schedule': search.get('first_bug_schedule', ''),
                  'tool_elapsed_seconds': search.get('tool_elapsed_seconds', ''),
                  'replay_status': '', 'replay_tries': 0}
        if search.get('dry_run_abort'):
            record['status'] = 'aborted_at_dry_run'
            rows.append(record)
            print('run %02d: aborted_at_dry_run' % number, flush=True)
            continue
        if search.get('validation_issue'):
            record['status'] = 'needs_inspection'
            rows.append(record)
            print('run %02d: needs_inspection (%s)' % (number, search['validation_issue']), flush=True)
            continue
        confirmed = False
        invalid = False
        tries = 0
        for index in range(1, CONFIG['replay_attempts'] + 1):
            replay = replay_attempt(attempt, pilot, CONFIG, 'period', SUBJECT, BINARY,
                                    build, driver, index)
            tries += 1
            if replay['status'] == 'confirmed':
                confirmed = True
                record['replay_status'] = 'confirmed'
                break
            if replay['status'] == 'dry_run_asan_abort':
                record['replay_status'] = 'dry_run_asan_abort'
                continue
            if replay['status'] == 'ran_without_expected_diagnostic':
                record['replay_status'] = 'invalid_replay'
                invalid = True
                break
            record['replay_status'] = replay['status']
            break
        record['replay_tries'] = tries
        record['status'] = ('completed' if confirmed else
                            ('invalid_replay' if invalid else 'replay_unverified_at_dry_run'))
        rows.append(record)
        print('run %02d: %s' % (number, record['status']), flush=True)

    columns = ['attempt', 'status', 'schedules', 'error_schedules', 'first_bug_schedule',
               'tool_elapsed_seconds', 'replay_status', 'replay_tries']
    with (work / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    counts = {status: sum(1 for r in rows if r['status'] == status)
              for status in ['completed', 'aborted_at_dry_run', 'invalid_replay',
                             'replay_unverified_at_dry_run', 'needs_inspection']}
    save(work / 'aggregate.json', {
        'attempts': len(rows), 'counts': counts,
        'completed_error_values': [r['error_schedules'] for r in rows
                                   if r['status'] == 'completed'],
        'completed_first_values': [r['first_bug_schedule'] for r in rows
                                   if r['status'] == 'completed'],
    })
    export(work, destination)
    print('Counts:', counts)
    print('Completed errors:', [r['error_schedules'] for r in rows if r['status'] == 'completed'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Append Table 2 local subset evidence to results/raw/measurements.csv."""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ['experiment_id', 'claim_id', 'benchmark', 'mode', 'run_id', 'metric',
           'value', 'unit', 'log_path', 'environment_path']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', default='results/raw/local-table2-local-comparison-20261118')
    parser.add_argument('--measurements', default='results/raw/measurements.csv')
    args = parser.parse_args()

    evidence = (ROOT / args.evidence).resolve()
    measurements = (ROOT / args.measurements).resolve()
    config = json.loads((evidence / 'config.json').read_text(encoding='utf-8'))
    experiment_id = config['experiment_id']
    claim_id = config['claim_id']

    with (evidence / 'summary.csv').open(encoding='utf-8', newline='') as handle:
        summary = list(csv.DictReader(handle))
    existing = []
    if measurements.exists():
        with measurements.open(encoding='utf-8-sig', newline='') as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != COLUMNS:
                raise SystemExit('Unexpected measurements.csv header')
            existing = list(reader)
    if any(row['experiment_id'] == experiment_id for row in existing):
        raise SystemExit('Experiment already present: ' + experiment_id)

    new_rows = []
    skipped = 0
    for row in summary:
        if row.get('status') in ('aborted_at_dry_run', 'invalid_replay',
                                 'replay_unverified_at_dry_run'):
            skipped += 1
            continue
        if not (row.get('schedules') or '').strip():
            skipped += 1
            continue
        method, case = row['method'], row['case']
        run_id = '%s-%s-run%02d' % (method, case, int(row['attempt']))
        log_rel = (evidence / 'runs' / method / case / ('run-' + row['attempt']) /
                   'search' / 'search.log').relative_to(ROOT).as_posix()
        env_rel = (evidence / 'manifest.json').relative_to(ROOT).as_posix()
        if not (ROOT / log_rel).is_file():
            raise SystemExit('Missing log: ' + log_rel)
        metrics = [
            ('total_schedules', row.get('schedules'), 'schedules'),
            ('buggy_schedules', row.get('error_schedules'), 'schedules'),
            ('timeouts', row.get('timeouts'), 'count'),
            ('tool_elapsed_seconds', row.get('tool_elapsed_seconds'), 'seconds'),
            ('wall_time_seconds', row.get('search_wrapper_seconds'), 'seconds'),
        ]
        if row.get('status') == 'completed' and (row.get('first_bug_schedule') or '').strip():
            metrics.append(('schedules_to_first_bug', row.get('first_bug_schedule'), 'schedules'))
        for metric, value, unit in metrics:
            if value is None or str(value).strip() == '':
                continue
            new_rows.append({
                'experiment_id': experiment_id, 'claim_id': claim_id,
                'benchmark': case, 'mode': method, 'run_id': run_id,
                'metric': metric, 'value': value, 'unit': unit,
                'log_path': log_rel, 'environment_path': env_rel,
            })

    with measurements.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in existing:
            writer.writerow({key: row[key] for key in COLUMNS})
        for row in new_rows:
            writer.writerow(row)
    print('Appended %d rows for %s; skipped %d attempts' % (
        len(new_rows), experiment_id, skipped))
    print('Total rows now: %d' % (len(existing) + len(new_rows)))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as error:
        print('Table 2 measurements build failed: ' + str(error), file=sys.stderr)
        sys.exit(1)

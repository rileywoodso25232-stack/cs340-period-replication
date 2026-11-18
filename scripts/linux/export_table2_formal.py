#!/usr/bin/env python3
"""Export small evidence of the Table 2 local subset, hash checked (3.6+)."""
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

source = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[2]
destination = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else (
    repo / 'results/raw/local-table2-local-comparison-20261118')
manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
status = manifest.get('status')
if status not in ('prepared', 'running', 'stopped_for_inspection',
                  'formal_completed', 'original_changed'):
    raise SystemExit('Unexpected manifest status: ' + str(status))
if destination.exists():
    raise SystemExit('Destination already exists: ' + str(destination))

MAX_BYTES = 2 * 1024 * 1024
SKIP_SUFFIXES = {'.bc', '.o', '.a', '.so', '.pyc'}
SKIP_PARTS = {'__pycache__'}
copied, excluded = {}, {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


destination.mkdir(parents=True)
for path in sorted(source.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(source)
    if set(relative.parts) & SKIP_PARTS:
        continue
    if path.open('rb').read(4) == b'\x7fELF':
        excluded[str(relative)] = {'reason': 'ELF executable', 'sha256': digest(path)}
        continue
    if path.suffix.lower() in SKIP_SUFFIXES:
        excluded[str(relative)] = {'reason': 'build artifact', 'sha256': digest(path)}
        continue
    if path.stat().st_size > MAX_BYTES:
        excluded[str(relative)] = {'reason': 'larger than 2 MiB', 'sha256': digest(path)}
        continue
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(path), str(target))
    checksum = digest(path)
    if digest(target) != checksum:
        raise SystemExit('Copy checksum mismatch: ' + str(relative))
    copied[str(relative)] = checksum

columns = ['method', 'case', 'attempt', 'status', 'schedules', 'error_schedules',
           'timeouts', 'first_bug_schedule', 'tool_elapsed_seconds',
           'search_wrapper_seconds', 'replay_status', 'replay_tries',
           'replay_child_exit', 'replay_wrapper_seconds', 'validation_issue']
rows = []
for record in manifest.get('runs', []):
    search = record.get('search') or {}
    replay = record.get('replay') or {}
    tries = record.get('replay_tries') or []
    if not replay and tries:
        replay = tries[-1]
    exits = replay.get('observed_child_exits') or []
    rows.append({
        'method': record.get('method'), 'case': record.get('case'),
        'attempt': record.get('run'), 'status': record.get('status'),
        'schedules': search.get('schedules', ''),
        'error_schedules': search.get('error_schedules', ''),
        'timeouts': search.get('timeouts', ''),
        'first_bug_schedule': search.get('first_bug_schedule', ''),
        'tool_elapsed_seconds': search.get('tool_elapsed_seconds', ''),
        'search_wrapper_seconds': search.get('wrapper_elapsed_seconds', ''),
        'replay_status': replay.get('status', ''),
        'replay_tries': len(tries),
        'replay_child_exit': exits[-1] if exits else '',
        'replay_wrapper_seconds': replay.get('wrapper_elapsed_seconds', ''),
        'validation_issue': search.get('validation_issue') or '',
    })
with (destination / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def mean_sd(values):
    values = [float(v) for v in values if v != '']
    if not values:
        return '', '', 0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, '', len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return mean, variance ** 0.5, len(values)


case_columns = ['method', 'case', 'total_attempts', 'completed', 'not_found',
                'aborted_at_dry_run', 'invalid_replay', 'replay_unverified',
                'search_valid', 'mean_schedules', 'sd_schedules', 'mean_error_schedules',
                'sd_error_schedules', 'mean_first_bug_schedule', 'sd_first_bug_schedule',
                'mean_tool_elapsed_seconds', 'sd_tool_elapsed_seconds']
aggregate = []
for method in manifest.get('methods', {}):
    for case in manifest.get('targets', {}):
        attempts = [r for r in rows if r['method'] == method and r['case'] == case]
        if not attempts:
            continue
        search_valid = [r for r in attempts if r['schedules'] != '']
        found = [r for r in attempts if r['status'] == 'completed']
        stats = {}
        for key in ['schedules', 'error_schedules']:
            stats[key] = mean_sd([r[key] for r in search_valid])
        stats['first'] = mean_sd([r['first_bug_schedule'] for r in found])
        stats['tool'] = mean_sd([r['tool_elapsed_seconds'] for r in search_valid])
        aggregate.append({
            'method': method, 'case': case, 'total_attempts': len(attempts),
            'completed': len(found),
            'not_found': sum(1 for r in attempts if r['status'] == 'not_found'),
            'aborted_at_dry_run': sum(1 for r in attempts if r['status'] == 'aborted_at_dry_run'),
            'invalid_replay': sum(1 for r in attempts if r['status'] == 'invalid_replay'),
            'replay_unverified': sum(1 for r in attempts if r['status'] == 'replay_unverified_at_dry_run'),
            'search_valid': len(search_valid),
            'mean_schedules': stats['schedules'][0], 'sd_schedules': stats['schedules'][1],
            'mean_error_schedules': stats['error_schedules'][0],
            'sd_error_schedules': stats['error_schedules'][1],
            'mean_first_bug_schedule': stats['first'][0],
            'sd_first_bug_schedule': stats['first'][1],
            'mean_tool_elapsed_seconds': stats['tool'][0],
            'sd_tool_elapsed_seconds': stats['tool'][1],
        })
with (destination / 'summary_by_case.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=case_columns)
    writer.writeheader()
    for row in aggregate:
        writer.writerow(row)

packaging = {
    'linux_full_evidence': str(source), 'manifest_status': status,
    'exported_utc': datetime.now(timezone.utc).isoformat(),
    'copied_files_sha256': copied, 'excluded_files': excluded,
    'all_copied_bytes_verified': True,
    'note': 'Table 2 local subset; binaries and build artifacts stay in Linux.',
}
(destination / 'packaging.json').write_text(
    json.dumps(packaging, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('Exported and verified {0} files; excluded {1}; status {2}'.format(
    len(copied), len(excluded), status))
print('Destination: ' + str(destination))
for row in aggregate:
    print('{method} {case}: total={total_attempts} completed={completed} '
          'not_found={not_found} dry-abort={aborted_at_dry_run} '
          'invalid={invalid_replay} mean schedules={mean_schedules} '
          'mean errors={mean_error_schedules} mean first={mean_first_bug_schedule}'.format(**row))

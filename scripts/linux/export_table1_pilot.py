#!/usr/bin/env python3
"""Export small evidence of a Table 1 pilot run, hash checked (Python 3.6+)."""
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
    repo / 'results/raw/local-table1-cve-pilot-20261117')
manifest_path = source / 'manifest.json'
if not manifest_path.is_file():
    raise SystemExit('No manifest.json in ' + str(source))
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
status = manifest.get('status')
if status not in ('prepared', 'running', 'stopped_for_inspection',
                  'pilot_completed', 'original_changed'):
    raise SystemExit('Unexpected manifest status: ' + str(status))
if destination.exists():
    raise SystemExit('Destination already exists, refusing to mix evidence: ' + str(destination))

MAX_BYTES = 2 * 1024 * 1024
SKIP_SUFFIXES = {'.bc', '.o', '.a', '.so', '.pyc', '.dylib', '.dll'}
SKIP_PARTS = {'__pycache__'}

copied = {}
excluded = {}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


destination.mkdir(parents=True)
for path in sorted(source.rglob('*')):
    if not path.is_file():
        continue
    relative = path.relative_to(source)
    if set(relative.parts) & SKIP_PARTS:
        continue
    head = path.open('rb').read(4)
    if head == b'\x7fELF':
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

# --- per-attempt summary -------------------------------------------------
attempt_columns = ['case', 'attempt', 'status', 'schedules', 'error_schedules',
                   'timeouts', 'first_bug_schedule', 'tool_elapsed_seconds',
                   'effective_depth_confirmed', 'search_wrapper_seconds',
                   'replay_confirmed', 'replay_child_exit',
                   'replay_wrapper_seconds', 'validation_issue']
rows = []
for record in manifest.get('runs', []):
    search = record.get('search') or {}
    replay = record.get('replay') or {}
    child_exits = replay.get('observed_child_exits') or []
    issue = search.get('validation_issue') or replay.get('validation_issue') or ''
    rows.append({
        'case': record.get('case'),
        'attempt': record.get('run'),
        'status': record.get('status'),
        'schedules': search.get('schedules', ''),
        'error_schedules': search.get('error_schedules', ''),
        'timeouts': search.get('timeouts', ''),
        'first_bug_schedule': search.get('first_bug_schedule', ''),
        'tool_elapsed_seconds': search.get('tool_elapsed_seconds', ''),
        'effective_depth_confirmed': search.get('effective_depth_confirmed', ''),
        'search_wrapper_seconds': search.get('wrapper_elapsed_seconds', ''),
        'replay_confirmed': replay.get('diagnostic_confirmed', ''),
        'replay_child_exit': child_exits[-1] if child_exits else '',
        'replay_wrapper_seconds': replay.get('wrapper_elapsed_seconds', ''),
        'validation_issue': issue,
    })

with (destination / 'summary.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=attempt_columns)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def mean_sd(values):
    values = [float(v) for v in values]
    if not values:
        return '', '', 0
    mean = sum(values) / len(values)
    if len(values) < 2:
        return mean, '', len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return mean, variance ** 0.5, len(values)


case_columns = ['case', 'completed_attempts', 'aborted_at_dry_run', 'total_attempts',
                'mean_schedules', 'sd_schedules', 'mean_error_schedules',
                'sd_error_schedules', 'mean_first_bug_schedule',
                'sd_first_bug_schedule', 'mean_tool_elapsed_seconds',
                'sd_tool_elapsed_seconds']
aggregate = []
for case in manifest.get('targets', {}) or {}:
    attempts = [r for r in rows if r['case'] == case]
    completed = [r for r in attempts if r['status'] == 'completed']
    schedules = mean_sd([r['schedules'] for r in completed if r['schedules'] != ''])
    errors = mean_sd([r['error_schedules'] for r in completed if r['error_schedules'] != ''])
    first = mean_sd([r['first_bug_schedule'] for r in completed if r['first_bug_schedule'] != ''])
    elapsed = mean_sd([r['tool_elapsed_seconds'] for r in completed
                       if r['tool_elapsed_seconds'] != ''])
    aggregate.append({
        'case': case, 'completed_attempts': len(completed),
        'aborted_at_dry_run': sum(1 for r in attempts if r['status'] == 'aborted_at_dry_run'),
        'total_attempts': len(attempts),
        'mean_schedules': schedules[0], 'sd_schedules': schedules[1],
        'mean_error_schedules': errors[0], 'sd_error_schedules': errors[1],
        'mean_first_bug_schedule': first[0], 'sd_first_bug_schedule': first[1],
        'mean_tool_elapsed_seconds': elapsed[0], 'sd_tool_elapsed_seconds': elapsed[1],
    })

with (destination / 'summary_by_case.csv').open('w', newline='', encoding='utf-8') as handle:
    writer = csv.DictWriter(handle, fieldnames=case_columns)
    writer.writeheader()
    for row in aggregate:
        writer.writerow(row)

packaging = {
    'linux_full_evidence': str(source),
    'manifest_status': status,
    'exported_utc': datetime.now(timezone.utc).isoformat(),
    'copied_files_sha256': copied,
    'excluded_files': excluded,
    'all_copied_bytes_verified': True,
    'note': 'Binaries and large build artifacts stay in Linux; this export keeps logs, '
            'configs, schedules and result JSON needed to trace every reported number.',
}
(destination / 'packaging.json').write_text(
    json.dumps(packaging, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print('Exported and verified {0} files; excluded {1}; status {2}'.format(
    len(copied), len(excluded), status))
print('Destination: ' + str(destination))
for row in aggregate:
    print('{case}: {completed_attempts}/{total_attempts} completed, '
          'mean schedules={mean_schedules}, mean errors={mean_error_schedules}, '
          'mean first={mean_first_bug_schedule}'.format(**row))

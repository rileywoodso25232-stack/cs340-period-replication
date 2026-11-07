#!/usr/bin/env python3
"""Read existing logs only. Preserve the original summary and all raw evidence."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile


def parse_log(raw):
    text = re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', raw)
    patterns = {'schedules': r'^Round\s+\d+\s+(\d+)\s*$',
                'error_schedules': r'Total Error Interleavings:\s*(\d+)',
                'timeouts': r'Total Timeouts Interleavings:\s*(\d+)'}
    result = {}
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.M)
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous footer: ' + name)
        result[name] = int(matches[0])
    if 'End Testing!' not in text or result['schedules'] <= 0:
        raise ValueError('Search did not finish or schedule count is invalid')
    if result['error_schedules'] > result['schedules'] or result['timeouts'] > result['schedules']:
        raise ValueError('Inconsistent footer counts')
    return result


def main():
    root = Path(sys.argv[1]).resolve()
    records, evidence = [], []
    with (root / 'summary.csv').open(newline='', encoding='utf-8') as source:
        original = list(csv.DictReader(source))
    for method in ('serial', 'period'):
        for group in range(1, 4):
            folder = root / method / ('group-' + str(group))
            path = folder / 'search.log'
            data = path.read_bytes()
            result = parse_log(data.decode('utf-8', errors='replace'))
            exit_code = int((folder / 'search.exit').read_text().strip())
            if exit_code != 0:
                raise ValueError('Nonzero driver exit: ' + str(folder))
            rows = [r for r in original if r['method'] == method and int(r['group']) == group]
            if len(rows) != 1:
                raise ValueError('Missing or ambiguous original summary row')
            result = dict(method=method, group=group, exit=exit_code, complete=True, **result)
            result['wrapper_elapsed_seconds'] = rows[0]['wrapper_elapsed_seconds']
            records.append(result)
            evidence.append({'log': str(path.relative_to(root)),
                             'sha256': hashlib.sha256(data).hexdigest()})
    output = Path(tempfile.mkdtemp(prefix='summary-check-', dir=str(root)))
    with (output / 'summary.corrected.csv').open('w', newline='', encoding='utf-8') as target:
        writer = csv.DictWriter(target, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    (output / 'audit.json').write_text(json.dumps({
        'reason': 'Old parser missed ANSI-prefixed test lines; counts now use the final Round footer',
        'raw_logs': evidence, 'experiments_rerun': False,
        'original_summary_preserved': True}, indent=2) + '\n', encoding='utf-8')
    shutil.copy2(str(Path(__file__).resolve()), str(output / Path(__file__).name))
    for row in records:
        print(json.dumps(row), flush=True)
    print('Corrected summary: ' + str(output / 'summary.corrected.csv'))
    return 0


if __name__ == '__main__':
    sys.exit(main())

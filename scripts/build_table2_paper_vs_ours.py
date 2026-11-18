#!/usr/bin/env python3
"""Build the Table 2 Paper vs Ours table from the exported summary."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'results/raw/local-table2-local-comparison-20261118'
SUMMARY = EVIDENCE / 'summary_by_case.csv'
OUT_CSV = ROOT / 'results/processed/table2-paper-vs-ours.csv'
OUT_MD = ROOT / 'results/processed/table2-paper-vs-ours.md'

# Table 2, p.9. For Serial/reorder_10 the paper reports % (no first bug), L
# (10,000 schedule limit reached) and 0 buggy schedules.
PAPER = {
    ('period', 'reorder_3'): {'schedules_to_first_bug': 6, 'total_schedules': 27,
                              'buggy_schedules': 6},
    ('serial', 'reorder_3'): {'schedules_to_first_bug': 10, 'total_schedules': 30,
                              'buggy_schedules': 10},
    ('period', 'reorder_4'): {'schedules_to_first_bug': 9, 'total_schedules': 100,
                              'buggy_schedules': 12},
    ('serial', 'reorder_4'): {'schedules_to_first_bug': 37, 'total_schedules': 384,
                              'buggy_schedules': 90},
    ('period', 'reorder_5'): {'schedules_to_first_bug': 12, 'total_schedules': 225,
                              'buggy_schedules': 20},
    ('serial', 'reorder_5'): {'schedules_to_first_bug': 283, 'total_schedules': 5040,
                              'buggy_schedules': 816},
    ('period', 'reorder_10'): {'schedules_to_first_bug': 27, 'total_schedules': 2350,
                               'buggy_schedules': 89},
    ('serial', 'reorder_10'): {'schedules_to_first_bug': None, 'total_schedules': 10000,
                               'buggy_schedules': 0},
}
METRICS = [('schedules_to_first_bug', 'first'), ('total_schedules', 'schedules'),
           ('buggy_schedules', 'error')]
COLUMNS = ['claim_id', 'mode', 'paper_reference', 'benchmark', 'metric', 'unit',
           'paper_value', 'our_mean', 'our_stddev', 'n', 'absolute_gap',
           'relative_gap_percent', 'summary_path', 'deviations', 'verdict']
COMMON = ('WSL2 kernel 6.18.58.1 vs paper Ubuntu 18.04; candidate IPC-compatible drivers; '
          '3 attempts per setting vs paper 10; reorder_10 costs ~125-145 s per search')


def load():
    with SUMMARY.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    return {(row['method'], row['case']): row for row in rows}


def verdict(gap, relative, stddev):
    if abs(gap) < 1e-9:
        return 'supported'
    if relative is not None and abs(relative) <= 5 and abs(gap) <= 5:
        return 'partially supported'
    return 'not supported'


def main():
    rows = load()
    output, md_rows = [], []
    for method in ['period', 'serial']:
        for case in ['reorder_3', 'reorder_4', 'reorder_5', 'reorder_10']:
            source = rows.get((method, case))
            if source is None:
                raise SystemExit('Missing summary row: %s %s' % (method, case))
            for metric, key in METRICS:
                paper = PAPER[(method, case)][metric]
                if paper is None:
                    # reorder_10 Serial: the paper found no bug; ours must also be not_found.
                    not_found = int(source['not_found'])
                    total = int(source['total_attempts'])
                    output.append({
                        'claim_id': 'C2', 'mode': method,
                        'paper_reference': 'Table 2 (p.9), CS.%s_bad row, Period/Serial column' % case,
                        'benchmark': case, 'metric': metric, 'unit': 'schedules',
                        'paper_value': '', 'our_mean': '', 'our_stddev': '', 'n': 0,
                        'absolute_gap': '', 'relative_gap_percent': '',
                        'summary_path': 'results/raw/local-table2-local-comparison-20261118/summary_by_case.csv',
                        'deviations': COMMON + '; paper reports % (no bug found)',
                        'verdict': 'consistent not found (%d/%d)' % (not_found, total),
                    })
                    md_rows.append((method, case, metric, 'not found',
                                    '%d/%d not found' % (not_found, total), '', '',
                                    'consistent not found'))
                    continue
                if metric == 'schedules_to_first_bug':
                    mean = source['mean_first_bug_schedule']
                    sd = source['sd_first_bug_schedule']
                    n = source['completed']
                else:
                    mean = source['mean_schedules' if metric == 'total_schedules'
                                  else 'mean_error_schedules']
                    sd = source['sd_schedules' if metric == 'total_schedules'
                                else 'sd_error_schedules']
                    n = source['search_valid']
                if mean == '':
                    mean_value = None
                    sd_value = None
                else:
                    mean_value = float(mean)
                    sd_value = float(sd) if sd != '' else 0.0
                if mean_value is None:
                    gap = None
                    relative = None
                    verdict_text = 'no numeric mean'
                else:
                    gap = mean_value - paper
                    relative = None if paper == 0 else gap / abs(paper) * 100.0
                    verdict_text = verdict(gap, relative, sd_value)
                    if method == 'serial' and case == 'reorder_10' and metric == 'total_schedules':
                        verdict_text = 'consistent (limit reached; ours=%.0f)' % mean_value
                output.append({
                    'claim_id': 'C2', 'mode': method,
                    'paper_reference': 'Table 2 (p.9), CS.%s_bad row, Period/Serial column' % case,
                    'benchmark': case, 'metric': metric, 'unit': 'schedules',
                    'paper_value': paper,
                    'our_mean': '' if mean_value is None else '%.4f' % mean_value,
                    'our_stddev': '' if mean_value is None else '%.4f' % (sd_value or 0),
                    'n': int(n),
                    'absolute_gap': '' if gap is None else '%.4f' % gap,
                    'relative_gap_percent': '' if relative is None else '%.2f' % relative,
                    'summary_path': 'results/raw/local-table2-local-comparison-20261118/summary_by_case.csv',
                    'deviations': COMMON + ('; paper value L means 10,000 schedule limit' if
                                            (case == 'reorder_10' and method == 'serial'
                                             and metric == 'total_schedules') else ''),
                    'verdict': verdict_text,
                })
                md_rows.append((method, case, metric, paper,
                                'None' if mean_value is None else '%.2f ± %.2f (n=%s)' % (
                                    mean_value, sd_value or 0, n),
                                '' if gap is None else '%.2f' % gap,
                                '' if relative is None else '%.2f%%' % relative,
                                verdict_text))
    with OUT_CSV.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in output:
            writer.writerow(row)
    lines = [
        '# Paper vs. Ours — Table 2 local subset (reorder thread series)',
        '',
        'Source: `results/raw/local-table2-local-comparison-20261118/summary_by_case.csv`.',
        'Paper values: Table 2, p.9. Three attempts per setting (course minimum); the',
        'paper used ten. `Serial / reorder_10` reaches the 10,000-schedule limit without',
        'finding the bug in the paper; our runs record a not_found outcome.',
        '',
        '| Method | Case | Metric | Paper | Ours | Abs. gap | Rel. gap | Verdict |',
        '|---|---|---|---:|---|---:|---:|---|',
    ]
    for method, case, metric, paper, ours, gap, relative, text in md_rows:
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            method, case, metric, paper, ours, gap, relative, text))
    lines += ['', 'No significance test is claimed; the paper gives no per-run SDs.']
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Wrote %d rows to %s and %s' % (len(output), OUT_CSV, OUT_MD))


if __name__ == '__main__':
    main()

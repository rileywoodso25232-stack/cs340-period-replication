#!/usr/bin/env python3
"""Build results/processed/paper_vs_ours.csv for the scoped Table 1 subset.

Paper values are from Table 1 (p.8): the CVE benchmark has only 2-thread
programs, so the paper reports Period and Serial in one combined column.
Our values come from results/processed/summary.csv (sample SD, n-1).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / 'results/processed/summary.csv'
OUT_CSV = ROOT / 'results/processed/paper_vs_ours.csv'
OUT_MD = ROOT / 'results/processed/table1-paper-vs-ours.md'

PAPER = {
    'CVE-2016-7911': {'schedules_to_first_bug': 3, 'total_schedules': 19,
                      'buggy_schedules': 8},
    'CVE-2016-9806': {'schedules_to_first_bug': 6, 'total_schedules': 42,
                      'buggy_schedules': 4},
    'CVE-2017-15265': {'schedules_to_first_bug': 11, 'total_schedules': 96,
                       'buggy_schedules': 1},
}
METRICS = ['schedules_to_first_bug', 'total_schedules', 'buggy_schedules']
CASES = ['CVE-2016-7911', 'CVE-2016-9806', 'CVE-2017-15265']
METHODS = ['period', 'serial']
EXCLUDED = {('serial', 'CVE-2017-15265')}
COLUMNS = ['claim_id', 'mode', 'paper_reference', 'benchmark', 'metric', 'unit',
           'paper_value', 'our_mean', 'our_stddev', 'n', 'absolute_gap',
           'relative_gap_percent', 'summary_path', 'deviations', 'verdict']

DEVIATION_COMMON = ('WSL2 kernel 6.18.58.1 vs paper Ubuntu 18.04/GCC 7.5/LLVM 10; '
                    'candidate IPC-compatible driver; sequential attempts; n as listed')
DEVIATIONS = {
    ('period', 'CVE-2016-7911'):
        DEVIATION_COMMON + '; 1 dry-run abort excluded (n=9 of 10 attempts)',
    ('period', 'CVE-2017-15265'):
        DEVIATION_COMMON + '; 1 invalid_replay excluded (early schedule did not replay); '
                           'one valid run had 3 buggy schedules',
    ('serial', 'CVE-2016-7911'):
        DEVIATION_COMMON + '; paper merges Period/Serial because all CVE programs have 2 '
                           'threads; candidate Serial identity not independently verified',
    ('serial', 'CVE-2016-9806'):
        DEVIATION_COMMON + '; paper merges Period/Serial because all CVE programs have 2 '
                           'threads; candidate Serial identity not independently verified',
    ('period', 'CVE-2016-9806'):
        DEVIATION_COMMON,
}
EXCLUDED_DEVIATION = (
    'Not evaluated: candidate Serial recorded non-reproducible failure schedules for this '
    'case (schedules 7 and 49 did not replay; only 11 did), so first-bug and buggy-schedule '
    'counts are not trustworthy. Evidence: results/raw/local-table1-local-runs-20261118-'
    'scoped-attempt1-stopped/README.md')


def load_summary():
    with SUMMARY.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    return {(row['mode'], row['benchmark'], row['metric']): row for row in rows}


def verdict(gap, relative, stddev):
    if abs(gap) < 1e-9:
        return 'supported'
    if relative is not None and abs(relative) <= 25 and stddev is not None and stddev <= 1:
        return 'partially supported'
    return 'not supported'


def main():
    summary = load_summary()
    output = []
    md_rows = []
    for method in METHODS:
        for case in CASES:
            for metric in METRICS:
                paper = PAPER[case][metric]
                if (method, case) in EXCLUDED:
                    output.append({
                        'claim_id': 'C1', 'mode': method,
                        'paper_reference': 'Table 1 (p.8), %s row, Period/Serial column' % case,
                        'benchmark': case, 'metric': metric, 'unit': 'schedules',
                        'paper_value': paper, 'our_mean': '', 'our_stddev': '', 'n': 0,
                        'absolute_gap': '', 'relative_gap_percent': '',
                        'summary_path': 'results/processed/summary.csv',
                        'deviations': EXCLUDED_DEVIATION,
                        'verdict': 'not evaluated (excluded)',
                    })
                    md_rows.append((method, case, metric, paper, '', '', '',
                                    'not evaluated (excluded)'))
                    continue
                row = summary.get((method, case, metric))
                if row is None:
                    raise SystemExit('Missing summary row: %s %s %s' % (method, case, metric))
                mean = float(row['mean'])
                stddev = float(row['stddev'])
                n = int(row['n'])
                gap = mean - paper
                relative = None if paper == 0 else gap / abs(paper) * 100.0
                entry = {
                    'claim_id': 'C1', 'mode': method,
                    'paper_reference': 'Table 1 (p.8), %s row, Period/Serial column' % case,
                    'benchmark': case, 'metric': metric, 'unit': 'schedules',
                    'paper_value': paper, 'our_mean': '%.4f' % mean,
                    'our_stddev': '%.4f' % stddev, 'n': n,
                    'absolute_gap': '%.4f' % gap,
                    'relative_gap_percent': '' if relative is None else '%.2f' % relative,
                    'summary_path': 'results/processed/summary.csv',
                    'deviations': DEVIATIONS.get((method, case), DEVIATION_COMMON),
                    'verdict': verdict(gap, relative, stddev),
                }
                output.append(entry)
                md_rows.append((method, case, metric, paper,
                                '%.2f ± %.2f (n=%d)' % (mean, stddev, n),
                                '%.2f' % gap, '' if relative is None else '%.2f%%' % relative,
                                entry['verdict']))

    with OUT_CSV.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in output:
            writer.writerow(row)

    lines = [
        '# Paper vs. Ours — scoped Table 1 subset',
        '',
        'Source: `results/processed/summary.csv` (sample SD, n-1); paper values from',
        'Table 1, p.8. The paper merges Period and Serial for the CVE benchmark because all',
        'programs have two threads. `Serial / CVE-2017-15265` is excluded; see the evidence',
        'README for the non-reproducible schedules.',
        '',
        '| Method | Case | Metric | Paper | Ours (mean ± sd, n) | Abs. gap | Rel. gap | Verdict |',
        '|---|---|---|---:|---|---:|---:|---|',
    ]
    for method, case, metric, paper, ours, gap, relative, verdict_text in md_rows:
        lines.append('| %s | %s | %s | %s | %s | %s | %s | %s |' % (
            method, case, metric, paper, ours, gap, relative, verdict_text))
    lines += [
        '',
        'Interpretation: exact schedule counts in most rows are consistent with a',
        'deterministic schedule count for a fixed input; the buggy-schedule counts for',
        '15265 (Period) and the candidate Serial rows vary slightly. No significance test',
        'is claimed: the paper does not provide per-run raw data or standard deviations.',
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Wrote %d rows to %s and %s' % (len(output), OUT_CSV, OUT_MD))


if __name__ == '__main__':
    main()

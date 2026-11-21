# Table 1 - Formal CVE Replication

Date: 2026-11-21

## Scope

We evaluated three selected benchmarks:

- CVE-2016-7911
- CVE-2016-9806
- CVE-2017-15265

## Methods

### PERIOD

- Depth: 5
- Search limit: 10,000
- 30 completed runs (10 per CVE)
- One additional aborted attempt retained
- Raw data: results/raw/table1-period-formal-20261121/
- Run status: audit-depth5/all-attempts.csv

### Serial-compatible baseline

- Depth: 5
- Search limit: 10,000
- 30 completed runs (10 per CVE)
- Raw data: results/raw/table1-serial-formal-20261121/
- Protocol: PROTOCOL.txt
- Individual search logs and error schedules retained
- Driver derived from the original run_OldPDS.py
- Compatibility repairs applied; complete equivalence
  to the paper implementation is not established

### Native baseline

- No PERIOD scheduling instrumentation
- AddressSanitizer enabled
- 3 groups per CVE, 10,000 executions per group
- 90,000 execution records
- Raw data: results/raw/native-cve-2026-11-14/

## Processed Results

Location: results/processed/table1-final/

- measurements.csv: 69 experimental records
- summary.csv: 9 statistical groups
- paper-vs-ours.csv: 24 paper comparisons
- native-group-audit.csv: Native execution audit
- native-exit-audit.md: exit-code interpretation

## Key Findings

Across the 18 controlled-method numerical comparisons,
14 matched the paper and 4 differed.

PERIOD and Serial report scheduling metrics.
Native reports uncontrolled execution metrics.

These different units must not be treated as identical.

Native identified 115 ASan errors in total.

Another 68 executions of CVE-2017-15265 exited
with code 1 without an ASan error flag.
Their detailed logs were not retained, so these
exits remain unclassified.

No Native exit-code-124 timeouts were recorded.

## Limitations

- The experiments cover three selected CVEs.
- The local environment differs from the original paper.
- The Serial driver required compatibility repairs.
- Native detection protocols may differ.
- Historical depth-extension results are excluded.

All observed differences are retained and reported.

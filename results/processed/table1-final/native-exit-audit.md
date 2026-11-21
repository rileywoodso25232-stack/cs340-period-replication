# Native Baseline Exit Audit

Date: 2026-11-21

## Coverage

Three CVE benchmarks, three groups per benchmark,
10,000 executions per group: 90,000 records in total.

## Findings

- ASan-identified errors: 115
- Exit code 1 without ASan identification: 68
- Exit code 124: 0

All 68 exit-code-1 records without an ASan flag
occurred in CVE-2017-15265.

## Classification

The original run_native.sh identifies ASan errors by
searching for the literal string "ERROR: AddressSanitizer".

An exit code of 1 without that identification does not
prove a specific memory error.

The script did not retain full logs for non-ASan runs.
Therefore, these 68 exits remain unclassified.

They are reported separately and are not added to
the 115 ASan-identified errors.

## Source

results/raw/native-cve-2026-11-14/run_native.sh
results/raw/native-cve-2026-11-14/*/group*/runs.csv

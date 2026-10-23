# Raw evidence

This folder initially contains **no measured observations**. Keep the CSV header.
Append actual numeric observations only, one metric per row:

`experiment_id,claim_id,benchmark,mode,run_id,metric,value,unit,log_path,environment_path`

- `experiment_id`: one frozen campaign/configuration; use a new ID for extensions
  or controlled checks. Never pool conditions under the same ID.
- `run_id`: unique independent repetition within the condition.
- `metric`: e.g. `schedules_to_first_bug`, `total_schedules`, `buggy_schedules`, or
  `wall_time_seconds`. Use the exact same metric and unit for paper comparisons.
- `value`: a measured finite number; missing/not-found results are not zero.
- `log_path`: repository-relative path to the original small execution log.
- `environment_path`: repository-relative path to the corresponding environment JSON.

Save exact commands, budgets, exit codes, failures and generated interleavings.
Small `.log` files are intentionally trackable. Large output stays in ignored
`bulk/`; if cited evidence is external, supply a stable retrieval script/location
and checksum and adapt the evidence validator explicitly.

The numeric CSV cannot represent censoring by itself. Keep every unsuccessful
attempt in a separate campaign outcome record and its original log, and define
the treatment before reporting an aggregate time-to-bug or detection rate.
The summarizer reports descriptive statistics only; it does not infer detection
rates, timeouts, claim verdicts or comparisons from absent observations.

# Main replication protocol (draft)

1. Read `docs/claims.md` and select exact rows from Tables 1 and 2 before final runs.
   Copy `config/experiments.example.json` to a named final JSON configuration and
   record the selection criteria, excluded cases, program paths and inputs.
2. Pin code/tool versions, error oracle, build flags, affinity and environment.
3. Match the paper's budgets and metrics for each selected subject. The reference
   depth limits are 5 for CVE examples and 3 for SCTBench, with 10,000 schedules.
4. Validate Native and any other selected baseline with the same error oracle.
   Describe how its run/time budget maps to PERIOD's schedule budget. A detection
   difference is not attributable to scheduling if the error oracles differ.
5. Execute at least three independent runs per setting (paper: ten). Reset program
   state and output locations, and retain every attempt including failures.
6. Preserve original logs, exact invocation, config, environment and group commit.
   Extract observations into `results/raw/measurements.csv`; do not guess values.
7. Run `python scripts/summarize.py`. Populate the Paper vs. Ours table using the
   same metric/unit and exact original row. Explain all mismatched settings.
8. For each discrepancy, complete `docs/analysis.md` with a controlled check.

`run_PDS.py -t` controls its subprocess timeout; it is not a substitute for the
overall schedule budget. Record both limits explicitly. Confirm current flags
against the pinned code before building the campaign runner.

Runtime estimates, selected subjects, the final campaign runner and validated
baseline invocation are pending the installation stage. No completed experiment
is implied by this protocol.

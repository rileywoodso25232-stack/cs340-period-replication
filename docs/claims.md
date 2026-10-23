# Claims to test (draft)

Select one to three claims, freeze exact subjects and settings, and link each claim
to a specific original figure/table. Current entries are proposals, not findings.

| ID | Scoped question | Original reference | Metrics | Current verdict |
| --- | --- | --- | --- | --- |
| C1 | Does PERIOD expose the selected real-world CVE examples within the reported search bounds? | Table 1, sections 4.1-4.3 | Schedules to first bug; total schedules; buggy schedules | Not evaluated |
| C2 | On a representative SCTBench subset, is the stated detection/search advantage observable against validated baselines? | Table 2, sections 4.2-4.3 | Same schedule metrics and buggy-program count; wall time separately | Not evaluated |

Original setup includes Ubuntu 18.04, GCC 7.5, LLVM 10.0, a 10,000-schedule
budget, depth limits of 5 (CVE) and 3 (SCTBench), and ten repeated runs. Record
deviations when using another setup or fewer runs. Three runs meet the course's
minimum; they do not duplicate the paper's ten-run protocol.

Final subject selection: pending. Include multiple bug types, thread counts and
hard cases; retain a record of failures and exclusions. Installation examples in
`test/` establish installation only and cannot stand in for all research claims.

Use supported, partially supported, not supported, or inconclusive as final
verdicts. Subset results support only the declared subset. No current experiment
establishes discovery of new vulnerabilities or superiority over all baselines.

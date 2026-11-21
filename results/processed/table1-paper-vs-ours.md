# Paper vs. Ours — scoped Table 1 subset

Source: `results/processed/summary.csv` (sample SD, n-1); paper values from
Table 1, p.8. The paper merges Period and Serial for the CVE benchmark because all
programs have two threads. `Serial / CVE-2017-15265` is excluded; see the evidence
README for the non-reproducible schedules.

| Method | Case | Metric | Paper | Ours (mean ± sd, n) | Abs. gap | Rel. gap | Verdict |
|---|---|---|---:|---|---:|---:|---|
| period | CVE-2016-7911 | schedules_to_first_bug | 3 | 3.00 ± 0.00 (n=9) | 0.00 | 0.00% | supported |
| period | CVE-2016-7911 | total_schedules | 19 | 19.00 ± 0.00 (n=9) | 0.00 | 0.00% | supported |
| period | CVE-2016-7911 | buggy_schedules | 8 | 8.00 ± 0.00 (n=9) | 0.00 | 0.00% | supported |
| period | CVE-2016-9806 | schedules_to_first_bug | 6 | 6.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| period | CVE-2016-9806 | total_schedules | 42 | 42.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| period | CVE-2016-9806 | buggy_schedules | 4 | 4.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| period | CVE-2017-15265 | schedules_to_first_bug | 11 | 11.00 ± 0.00 (n=9) | 0.00 | 0.00% | supported |
| period | CVE-2017-15265 | total_schedules | 96 | 96.00 ± 0.00 (n=9) | 0.00 | 0.00% | supported |
| period | CVE-2017-15265 | buggy_schedules | 1 | 1.22 ± 0.67 (n=9) | 0.22 | 22.22% | partially supported |
| serial | CVE-2016-7911 | schedules_to_first_bug | 3 | 3.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| serial | CVE-2016-7911 | total_schedules | 19 | 19.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| serial | CVE-2016-7911 | buggy_schedules | 8 | 7.90 ± 0.32 (n=10) | -0.10 | -1.25% | partially supported |
| serial | CVE-2016-9806 | schedules_to_first_bug | 6 | 6.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| serial | CVE-2016-9806 | total_schedules | 42 | 42.00 ± 0.00 (n=10) | 0.00 | 0.00% | supported |
| serial | CVE-2016-9806 | buggy_schedules | 4 | 4.10 ± 0.32 (n=10) | 0.10 | 2.50% | partially supported |
| serial | CVE-2017-15265 | schedules_to_first_bug | 11 |  |  |  | not evaluated (excluded) |
| serial | CVE-2017-15265 | total_schedules | 96 |  |  |  | not evaluated (excluded) |
| serial | CVE-2017-15265 | buggy_schedules | 1 |  |  |  | not evaluated (excluded) |

Interpretation: exact schedule counts in most rows are consistent with a
deterministic schedule count for a fixed input; the buggy-schedule counts for
15265 (Period) and the candidate Serial rows vary slightly. No significance test
is claimed: the paper does not provide per-run raw data or standard deviations.

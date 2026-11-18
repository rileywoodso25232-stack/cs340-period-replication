# Paper vs. Ours — Table 2 local subset (reorder thread series)

Source: `results/raw/local-table2-local-comparison-20261118/summary_by_case.csv`.
Paper values: Table 2, p.9. Three attempts per setting (course minimum); the
paper used ten. `Serial / reorder_10` reaches the 10,000-schedule limit without
finding the bug in the paper; our runs record a not_found outcome.

| Method | Case | Metric | Paper | Ours | Abs. gap | Rel. gap | Verdict |
|---|---|---|---:|---|---:|---:|---|
| period | reorder_3 | schedules_to_first_bug | 6 | 6.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_3 | total_schedules | 27 | 27.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_3 | buggy_schedules | 6 | 6.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_4 | schedules_to_first_bug | 9 | 9.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_4 | total_schedules | 100 | 100.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_4 | buggy_schedules | 12 | 12.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_5 | schedules_to_first_bug | 12 | 12.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_5 | total_schedules | 225 | 225.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_5 | buggy_schedules | 20 | 20.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_10 | schedules_to_first_bug | 27 | 27.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_10 | total_schedules | 2350 | 2350.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| period | reorder_10 | buggy_schedules | 89 | 90.00 ± 0.00 (n=3) | 1.00 | 1.12% | partially supported |
| serial | reorder_3 | schedules_to_first_bug | 10 | 10.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_3 | total_schedules | 30 | 30.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_3 | buggy_schedules | 10 | 10.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_4 | schedules_to_first_bug | 37 | 47.00 ± 0.00 (n=3) | 10.00 | 27.03% | not supported |
| serial | reorder_4 | total_schedules | 384 | 384.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_4 | buggy_schedules | 90 | 90.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_5 | schedules_to_first_bug | 283 | 283.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_5 | total_schedules | 5040 | 5040.00 ± 0.00 (n=3) | 0.00 | 0.00% | supported |
| serial | reorder_5 | buggy_schedules | 816 | 816.67 ± 2.08 (n=3) | 0.67 | 0.08% | partially supported |
| serial | reorder_10 | schedules_to_first_bug | not found | 3/3 not found |  |  | consistent not found |
| serial | reorder_10 | total_schedules | 10000 | 10001.00 ± 0.00 (n=3) | 1.00 | 0.01% | consistent (limit reached; ours=10001) |
| serial | reorder_10 | buggy_schedules | 0 | 0.00 ± 0.00 (n=3) | 0.00 |  | supported |

No significance test is claimed; the paper gives no per-run SDs.

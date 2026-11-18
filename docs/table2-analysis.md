# Table 2 discrepancy analysis — SCTBench reorder subset

Claim C2: on a representative SCTBench subset, is the stated detection/search
advantage observable against valid baselines?

Data: `local-table2-local-comparison-20261118` — four reorder thread-count programs,
Period and Serial, three attempts each, depth 3, budget 10000. Paper reference:
Table 2, p.9. Evidence:
`results/raw/local-table2-local-comparison-20261118/README.md`.

## Overall verdict for C2

**Partially supported (scoped subset).** The central parallel-vs-serial phenomenon
is reproduced: as the thread count grows, Serial needs far more schedules than
Period, and at reorder_10 Serial does not find the bug within the 10,000-schedule
limit while Period needs 2,350. Period's first/total/buggy counts match the paper
exactly for reorder_3/4/5 and differ by one buggy schedule for reorder_10. The
candidate Serial matches exactly for reorder_3, but its first-bug count for
reorder_4 is 47 instead of 37 and its reorder_5 buggy count varies slightly.

## Schedule counts and the parallel advantage

| Case | Period (ours) | Serial (ours) | Paper Period → Serial | Reduction |
|---|---:|---:|---|---:|
| reorder_3 | 27 | 30 | 27 → 30 | 10.0% |
| reorder_4 | 100 | 384 | 100 → 384 | 74.0% |
| reorder_5 | 225 | 5040 | 225 → 5040 | 95.5% |
| reorder_10 | 2350 | 10001 (not found) | 2350 → L | — |

The ranking and the growth trend match the paper. This is the strongest part of
C2: Period's schedule count grows far more slowly with thread count than Serial's.

## C2-P1 — Period on reorder_3/4/5

- Paper: 6/27/6, 9/100/12, 12/225/20.
- Ours: 6/27/6, 9/100/12, 12/225/20 (sd 0, n=3).
- Gaps: zero on all nine metrics.
- Verdict: **supported** within the three-attempt subset.
- Limitation: n=3; exact equality of schedule counts does not prove scheduling
  implementation correctness.

## C2-P2 — Period on reorder_10

- Paper: 27 / 2350 / 89.
- Ours: 27 / 2350 / 90 (sd 0, n=3).
- Gap: first and total exact; buggy +1 (+1.12%).
- Hypothesis: one schedule at the boundary is classified differently; the exact
  cause is not localized.
- Verdict: **partially supported** (first/total exact, buggy differs by one).

## C2-S1 — Serial on reorder_3

- Paper: 10 / 30 / 10; ours: 10 / 30 / 10 (sd 0, n=3).
- Verdict: **supported**.

## C2-S2 — Serial on reorder_4

- Paper: 37 / 384 / 90; ours: 47 / 384 / 90 (sd 0, n=3).
- Gap: first-bug +10 (+27.0%); total and buggy exact.
- Hypothesis: the candidate Serial driver records/orders schedules differently;
  first-bug is the earliest saved failure index, not necessarily the same search
  order as the paper's Serial. The candidate Serial identity is not independently
  proven. A driver-order explanation is plausible but unverified.
- Verdict: **not supported** for the first-bug metric; total/buggy supported.
- Limitation: a controlled check with the original Serial implementation was not
  possible locally (see the Table 1 environment/driver discussion).

## C2-S3 — Serial on reorder_5

- Paper: 283 / 5040 / 816; ours: 283 / 5040 / 816.67 ± 2.08 (n=3).
- First and total exact; buggy counts were 815, 816 and 819.
- Verdict: **partially supported** — the ±2 variation is small but the paper's
  single value is not reproduced exactly in every run.
- Limitation: n=3; runtime ~350 s per run, so more repeats were not attempted.

## C2-S4 — Serial on reorder_10

- Paper: `%` (no bug) / `L` (10,000 limit) / 0.
- Ours: 3/3 runs reached 10001 schedules with zero buggy schedules; no first bug.
- Verdict: **consistent not found**; the one-schedule difference at the limit is
  a driver counting-boundary detail, not a different outcome.
- Limitation: a not-found result within the budget is not proof that no bug exists;
  it is a censored observation, reported as such.

## Why C2 is only partially supported

1. **Subset**: four reorder programs of the same bug type (AF), not the full
   SCTBench table; selection bias limits generalization.
2. **Repetitions**: three attempts (course minimum) instead of ten; no significance
   claims, and the small Serial variation cannot be characterized precisely.
3. **Candidate Serial**: the reorder_4 first-bug difference and reorder_5 buggy
   variation are consistent with a candidate-driver identity/order issue; the
   original paper Serial is not available locally.
4. **Environment**: WSL2 kernel 6.18 vs Ubuntu 18.04; one timeout parameter was
   raised to 600 s for reorder_5, which affects runtime only, not the metric.
5. **No controlled check for the reorder_4 first-bug offset**: unlike the 15265
   checks, this discrepancy was not isolated experimentally; it remains a
   documented limitation rather than an explained cause.

## Timing (descriptive only)

| Case | Period tool seconds | Serial tool seconds |
|---|---:|---:|
| reorder_3 | 1.72 | 3.11 |
| reorder_4 | 5.18 | 32.58 |
| reorder_5 | 10.90 | 349.78 |
| reorder_10 | 120.85 | 125.05 (not found) |

The paper's Table 2 does not report these times; they are descriptive and
host-dependent, not a speed claim.

## Interpretation rules kept

- Not-found is a censored observation, not a zero first-bug value.
- Schedule counts, buggy counts and timing are reported separately.
- No significance test is claimed; the paper gives no per-run SDs.
- The stopped attempt (300 s timeout) is kept separately and not merged.

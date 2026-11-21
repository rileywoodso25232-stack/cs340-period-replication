# Discrepancy analysis — scoped Table 1 reproduction

Data source: formal scoped experiment `local-table1-local-runs-20261118-scoped`
(50 attempts: PERIOD on three CVEs, Serial on 7911/9806; depth 5, budget 10000,
10 attempts per case). Values: `results/processed/summary.csv`; comparison:
`results/processed/paper_vs_ours.csv`. Evidence:
`results/raw/local-table1-local-runs-20261118-scoped/README.md`.

Paper reference: Table 1, p.8. The CVE benchmark programs are all two-thread
programs, so the paper reports Period and Serial in one combined column and says
their results are "exactly the same".

## Overall verdict for C1

**Partially supported (scoped subset).** The first-bug and total-schedule counts
match the paper exactly for every evaluated case. The buggy-schedule count matches
exactly for Period on 7911/9806, but shows small variation for Serial on 7911/9806
and a larger, run-dependent variation for Period on 15265. Serial on 15265 is not
evaluated because the candidate Serial driver recorded non-reproducible schedules.
No claim is made about the paper's full CVE benchmark or about method superiority.

## C1-P1 — Period, CVE-2016-7911

- Original: Table 1, 7911 row, Period/Serial column: 3 / 19 / 8 (first / total / buggy).
- Ours: 3 / 19 / 8, sample SD 0 / 0 / 0, n = 9 (one dry-run ASan abort excluded).
- Gaps: 0 / 0 / 0.
- Setting differences: WSL2 kernel 6.18.58.1 instead of the paper's Ubuntu 18.04;
  candidate IPC-compatible driver; 9 valid attempts instead of 10.
- Hypothesis: the schedule count for this fixed input is deterministic and the
  implementation reproduces it. The dry-run abort is a separate target-startup
  instability, not a schedule result.
- Evidence: nine identical search results and nine confirmed replays in the
  evidence directory.
- Verdict: **supported** for the three schedule metrics.
- Limitation: n = 9; one attempt did not reach a controlled search.

## C1-P2 — Period, CVE-2016-9806

- Original: 6 / 42 / 4.
- Ours: 6 / 42 / 4, SD 0 / 0 / 0, n = 10.
- Gaps: 0 / 0 / 0.
- Verdict: **supported**.
- Limitation: same environment/deviation caveats as C1-P1.

## C1-P3 — Period, CVE-2017-15265

- Original: 11 / 96 / 1.
- Ours: 11 / 96 / 1.222 ± 0.667, n = 9. Absolute error-schedule gap +0.222
  (+22.2%); first and total are exact.
- One further attempt was recorded as `invalid_replay`: search reported
  96 / 2 / first 6, but the saved first failure (schedule 6) did not reproduce.
  It is kept in `summary.csv` but excluded from the mean; it is not recorded as
  zero and not replaced.
- Hypothesis: the target's UAF has a timing-dependent early trigger. A schedule
  that appears to fail during a long search sequence may not fail when replayed
  in a fresh process/IPC namespace; the same case sometimes also aborts during the
  uncontrolled dry run.
- Evidence: in one affected attempt, schedules 7 and 49 replayed with target exit
  0, while schedule 11 replayed with the expected heap-use-after-free and exit -6.
  The exit codes are from `target-exits.jsonl`, not inferred from parsing.
- Controlled check (stage 9): solo repetition without interleaving (CC1) and same-vs-fresh
  namespace replay (CC2), described below. Namespace/state isolation was **not** supported
  as the cause; interleaving remains a plausible but unproven factor.
- Verdict: **partially supported** — first/total exact; buggy count and attempt
  completion are not fully stable.
- Limitation: one invalid attempt; the mechanism is not fully localized.

## C1-S1 — Serial, CVE-2016-7911

- Original: 3 / 19 / 8 (paper merges Period and Serial).
- Ours: 3 / 19 / 7.9 ± 0.316, n = 10. Absolute buggy gap −0.1 (−1.25%).
- One run reported 7 buggy schedules, the other nine reported 8.
- Hypothesis: small execution-time variation changes whether one borderline
  schedule is classified as buggy; first/total remain deterministic.
- Verdict: **partially supported**.
- Limitation: the candidate Serial driver identity is not independently proven;
  the paper's exact-equality statement is not fully reproduced.

## C1-S2 — Serial, CVE-2016-9806

- Original: 6 / 42 / 4.
- Ours: 6 / 42 / 4.1 ± 0.316, n = 10. Absolute buggy gap +0.1 (+2.5%).
- One run reported 5 buggy schedules, the other nine reported 4.
- Verdict: **partially supported**; same limitations as C1-S1.

## C1-X — Serial, CVE-2017-15265 (excluded)

- The candidate Serial driver recorded early "failures" at schedules 7 and 49
  that did not replay (target exit 0), while schedule 11 replayed as the expected
  heap-use-after-free. Its first-bug and buggy-schedule counts for this case are
  therefore not trustworthy.
- No value is entered in `paper_vs_ours.csv`; verdict **not evaluated (excluded)**.
- Evidence: `results/raw/local-table1-local-runs-20261118-scoped-attempt1-stopped/README.md`
  and the earlier attempt record.
- This is a scope limitation, not a claim that Serial cannot find the bug.

## C1-EQ — Paper's "Period and Serial are exactly the same"

- On 7911/9806, first-bug and total schedules are identical between our Period and
  Serial runs; buggy schedules differ by ±1 in one run each (7.9 vs 8, 4.1 vs 4).
- On 15265, the candidate Serial is excluded, so the equality cannot be tested for
  all three cases.
- Verdict: **partially supported** — equality holds for the deterministic schedule
  totals and first-bug counts on two cases, but not exactly for every repeat and
  not for the full three-case set.

## Timing (descriptive only)

- Period tool means: 7911 7.27 s, 9806 4.59 s, 15265 4.01 s.
- Serial means: 7911 8.21 s, 9806 4.75 s.
- The paper's Table 1 does not report these wall/tool times, and hosts differ.
  Timing is reported for transparency only; it is not used to claim a speedup.

## Why this is not simply "our environment is broken"

- The same binary and driver produce the paper's exact schedule counts in most
  runs; 48/50 formal attempts reached valid search data, with zero timeouts.
- The teammate's independent Docker/WSL2 batch also observed one ASan abort in the
  10 depth-5 attempts and error counts 2/1/1 for 15265, so the instability is not
  unique to this machine.
- The invalid replay was verified from the target's actual exit code (0 vs -6) and
  ASan report; it is not a parsing or arithmetic bug in the analysis scripts.

## Plausible causes, in order of evidence

1. **Target-level timing nondeterminism**: the UAF can fire during the dry run or
   on an early schedule that does not replay.
2. **Search/replay state difference**: the search runs many schedules in one
   sequence; replay starts a fresh process and IPC namespace. A failure may depend
   on state or timing that the saved schedule does not encode.
3. **Candidate driver identity**: the IPC-compatible patch is teammate-derived; the
   Period patch preserved the protected AST, but Serial identity is unverified.
4. **Environment deviation**: WSL2 kernel 6.18 vs Ubuntu 18.04, and no independent
   per-thread SCHED_DEADLINE verification, may amplify timing variation. This is
   not demonstrated as the root cause.

## Controlled checks performed (stage 9)

### CC1 — CVE-2017-15265 alone (changed factor: no interleaving)

- Setup: same prepared driver/target hashes, depth 5, budget 10000, 10 attempts, replay
  policy unchanged; only the method/subject ordering differs.
- Result: 9/10 completed, 1 dry-run ASan abort, 0 invalid replays; all nine completed
  attempts are 96 / 1 / first 11, with 1 buggy schedule each.
- Interleaved formal batch for comparison: 9 completed, 0 dry-run abort, 1 invalid
  replay; errors were 1 in eight runs and 3 in one run.
- Interpretation: the early false-positive appeared only in the interleaved batch in
  this sample, so interleaving/context remains a plausible contributor; the dry-run
  abort persisted when the case ran alone, so it is not caused by interleaving. n=10
  per batch, so the ordering effect is not established.
- Evidence: `results/raw/local-table1-15265-solo-20261118/README.md`.

### CC2 — Same vs fresh IPC namespace (changed factor: replay state)

- Setup: five trials, each running one search and then replaying that search's first
  saved failure twice — once in the same IPC namespace/state immediately after the
  search, once in a fresh namespace. Driver, target, depth, budget and machine fixed.
- Result: 4 comparable trials (one search dry-run abort); same-namespace confirmed
  3/4, fresh-namespace confirmed 4/4. The one same-namespace miss was a replay dry-run
  ASan abort, not a failure to reproduce after a complete reproduction run.
- Interpretation: the hypothesis that search/replay state isolation causes the
  non-reproducible records is **not supported**; fresh replay was at least as good.
  Normal search failures replay in a fresh namespace, so the rare early record is more
  likely a target-timing false positive than a lost-state artifact.
- Evidence: `results/raw/local-table1-15265-namespace-20261118/README.md`.
- A first run of this check failed because the generated shell invoked the Python
  observer directly (rc=126); the failed evidence is kept separately and is not used.

### Remaining uncertainty

- The environment (WSL2 kernel 6.18 vs Ubuntu 18.04) and the teammate-derived driver
  patch are not isolated by these checks.
- No native Ubuntu/Docker comparison was available on this machine; the candidate
  Serial identity remains unverified.
- The exact mechanism of the rare early false positive is still unresolved; the
  conclusion is limited to "not explained by namespace/state isolation".

## Interpretation rules kept

- Invalid/timeout attempts are reported as such; they are not recorded as zero.
- Schedule counts, buggy counts and timing are reported separately.
- No significance test is claimed: the paper gives no per-run raw data or SDs.
- Exploratory diagnostics are separate from the formal batch.

## Supplementary Table 1 archive — 2026-11-21

This section documents an independent Table 1 experiment archive. It supplements, but does not replace or pool with, the `local-table1-local-runs-20261118-scoped` experiment analyzed above.

### Experimental scope

The additional archive covers CVE-2016-7911, CVE-2016-9806, and CVE-2017-15265.

- PERIOD: depth 5, search budget 10,000, 30 completed runs across three CVEs; one additional aborted attempt was retained.
- Serial-compatible: depth 5, search budget 10,000, 30 completed runs using a shared-memory-compatible candidate driver.
- Native: three groups of 10,000 executions per CVE, totaling 90,000 execution records, with AddressSanitizer used for error identification.

### Controlled scheduling results

The following values represent mean schedules to first bug / total schedules / buggy schedules. The paper's three reference values are listed first.

| CVE | Paper | PERIOD (new) | Serial-compatible (new) |
| --- | --- | --- | --- |
| 2016-7911 | 3 / 19 / 8 | 3 / 19 / 8 | 3 / 19 / 8.2 |
| 2016-9806 | 6 / 42 / 4 | 6.4 / 42 / 3.9 | 6 / 42 / 4 |
| 2017-15265 | 11 / 96 / 1 | 11 / 96 / 1 | 11 / 96 / 1.2 |

Among the 18 controlled-method numerical comparisons, 14 match the paper and four differ.

The differences are:

- PERIOD, CVE-2016-9806: first-bug schedules 6.4 versus 6 (+0.4, +6.67%); buggy schedules 3.9 versus 4 (-0.1, -2.5%).
- Serial-compatible, CVE-2016-7911: buggy schedules 8.2 versus 8 (+0.2, +2.5%).
- Serial-compatible, CVE-2017-15265: buggy schedules 1.2 versus 1 (+0.2, +20%).

All six controlled-method groups reproduce the paper's total schedule counts. These numerical agreements do not establish full implementation equivalence.

### Relationship to the earlier scoped experiment

The earlier formal scoped batch contained 50 attempts and 48 observations included in the corresponding statistical analysis. The new archive contains 60 completed controlled-method runs, covering Serial-compatible results for all three selected CVEs.

The earlier experiment excluded Serial on CVE-2017-15265 because of non-reproducible candidate-driver behavior. The new archive records ten completed Serial-compatible runs for this CVE, with a mean buggy-schedule count of 1.2.

This is additional evidence from a separate configuration and execution batch. It does not retroactively validate the excluded earlier runs or demonstrate that the earlier replay instability has been eliminated.

### Native baseline and classification limitations

The Native measurements are uncontrolled executions rather than controlled scheduling trials. Their execution counts must not be directly equated with PERIOD or Serial schedule counts.

Across 90,000 Native execution records:

- 115 errors were identified by AddressSanitizer.
- Another 68 executions of CVE-2017-15265 exited with code 1 without an ASan identification flag.
- These 68 exits remain unclassified and are excluded from the ASan-confirmed error count.
- No exit-code-124 timeouts were recorded.

The retained evidence does not establish the cause of the 68 unclassified exits. Native comparisons are therefore descriptive and protocol-dependent.

### Interpretation and limitations

The supplementary archive supports the reproducibility of several reported Table 1 scheduling counts, but does not prove complete equivalence with the original paper.

The Serial-compatible driver includes shared-memory ABI repairs. The source comparison did not identify scheduling-search algorithm changes, but full behavioral equivalence has not been established.

The local environment and execution protocols differ from the original experiment. The numerical results should be interpreted within the declared experimental scope. No pooled statistical estimate is computed across the earlier and newer batches.

**Updated C1 assessment: partially supported (scoped).** The new evidence strengthens coverage of the selected CVEs without removing the documented methodological limitations.

### Evidence and integrity

- [Final archive overview](table1-final/README.md)
- [Processed summary](../results/processed/table1-final/summary.csv)
- [Paper vs. Ours](../results/processed/table1-final/paper-vs-ours.csv)
- [Native exit audit](../results/processed/table1-final/native-exit-audit.md)
- [Serial driver provenance](table1-final/driver-provenance/README.md)
- [Package SHA256 manifest](../results/audit/table1-final/PACKAGE-SHA256.txt)

On 2026-11-21, all 785 file entries in the package manifest were verified against the GitHub `table1-integration` branch: 785 passed, zero failed. This establishes byte-level archive integrity, not experimental or statistical correctness.

# Discrepancy analysis worksheet

No results are available yet. Complete one record for each tested claim or
material discrepancy. Explanations remain hypotheses until checked.

## Record template

- Claim ID and exact original table/figure row:
- Original metric, unit, configuration and value:
- Our mean, sample standard deviation and independent run count:
- Raw measurement rows, logs, environment and code commit:
- Absolute gap: `our_mean - paper_value`.
- Relative gap: `(our_mean - paper_value) / abs(paper_value) * 100%`.
  If the paper value is zero, report relative gap as undefined.
- Setting differences that limit comparability:
- Proposed explanation:
- Controlled check: one changed factor, otherwise fixed settings:
- Evidence and whether the check supports the explanation:
- Verdict: supported / partially supported / not supported / inconclusive.
- Limitation and next check:

## Interpretation rules

1. Separate schedules-to-bug from wall-clock cost and from distinct bug counts.
2. A timeout is not automatically a deadlock or confirmed bug. Inspect and replay.
3. A missed bug within a budget is not proof that no bug exists.
4. If no bug is found, do not invent a numeric time-to-bug. Record censoring and
   budget exhaustion in the log; document the chosen treatment in the analysis.
5. Different hardware is a deviation, not a demonstrated explanation by itself.
6. Deterministic schedule counts may have standard deviation zero; execution time
   can still vary. Do not manufacture variation.
7. Multiple failing schedules may expose the same root cause. Report both clearly.
8. Keep exploratory/debug runs separate from the frozen final experiment.

# CS340: PERIOD Replication

Group reproduction of **Controlled Concurrency Testing via Periodical Scheduling**
(ICSE 2022), by Cheng Wen et al.

**Status: repository scaffold. No reproduction results have been collected.**
The paper choice is provisional. The upstream environment, smoke test, baselines,
and final benchmark selection still need validation.

- Paper: https://wcventure.github.io/pdf/ICSE2022_PERIOD.pdf
- Original implementation: https://github.com/wcventure/PERIOD
- Pinned starting commit: `cb8deb9a176e5bb292d70d46557dd61dc0e98069`
- Group repository: https://github.com/rileywoodso25232-stack/cs340-period-replication
- New to GitHub? Start with [the Chinese guide](GETTING_STARTED.zh-CN.md).

## Research scope

We plan a reduced-scale replication of selected rows of Tables 1 and 2. We will
measure schedules to first bug, total schedules, and buggy schedules, and record
wall-clock time separately. The final subset must cover multiple bug types and
thread counts; it must be selected and recorded before collecting final results.

Native execution is a planned local baseline. Other baselines, including Serial,
are pending availability checks. Until they run under comparable settings, no
comparative superiority claim is established. See [claims](docs/claims.md).

## Layout

```text
config/                 Pinned upstream reference and draft experiment settings
docs/                   Claims, team, plan, environment, deviations, analysis
environment/            Actual environment records and environment setup notes
experiments/smoke/      Installation validation procedure
experiments/baseline/   Main replication and baseline protocol
experiments/extension/  Single-factor extension protocol
scripts/                Source retrieval, environment capture, checks, statistics
src/                    Group-authored adapters and instrumentation, when needed
third_party/            Upstream source fetched locally; excluded from group Git
licenses/               Preserved PERIOD license
results/raw/            Measurements and small, directly cited execution logs
results/processed/      Recomputed statistics and Paper vs. Ours tables
results/figures/        Figures generated from processed data
report/                 English report outline and reference bibliography
presentation/           Presentation plan; separate teacher instructions pending
.github/                Issue and pull request templates
```

## Repository helpers

The helper scripts use **Python 3.10+ and the standard library**; Git is also
required for source retrieval. These are scaffold requirements, not a validated
PERIOD environment. Run from the repository root:

```sh
python scripts/check_repository.py
python scripts/capture_environment.py
python scripts/fetch_upstream.py
```

Expected outputs:

- Repository checks report missing files, invalid configuration, or oversized files.
- Environment capture writes a timestamped JSON file in `environment/records/`.
- Source retrieval checks out the exact upstream commit in `third_party/PERIOD/`.

Retrieval needs network access. Its duration depends on the download; no measured
runtime is available yet. It does not install LLVM, build PERIOD, or run benchmarks.
Upstream source is credited in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## PERIOD setup and smoke test

Use a Linux environment matching the original artifact as closely as practical.
Follow [environment instructions](environment/README.md), then
[the smoke-test procedure](experiments/smoke/README.md). Docker alone does not
pin the host kernel. Record the host/guest kernel and container image digest.

Build/run commands and elapsed times must be validated and documented during
environment setup. This scaffold does not claim clean-machine reproducibility of
the research artifact yet.

## Measurements and analysis

1. Freeze the cases, modes, budgets, repeats, and error oracle in `config/`.
2. Follow [the main experiment protocol](experiments/baseline/README.md).
3. Save original logs and an environment record for every measurement.
4. Append measured observations to `results/raw/measurements.csv`.
5. Compute statistics with `python scripts/summarize.py`.
6. Fill `results/processed/paper_vs_ours.csv` and use
   [the discrepancy analysis worksheet](docs/analysis.md).

The summarizer requires at least three independent runs per group. It creates
`results/processed/summary.csv`. With the initial empty input, it exits with a
clear no-data message. No example observations are mixed with research data.

## Collaboration and delivery

Read [CONTRIBUTING.md](CONTRIBUTING.md). Each member contributes from their own
GitHub account. Every project commit message, including merge commits, contains
the committing member's student ID and full name. Push meaningful progress each
week before the teacher's Sunday 23:59 check; late pushes cannot repair a missed week.

Track actual work in [team contributions](docs/team.md),
[the weekly log](docs/weekly-log.md), and [the project plan](docs/project-plan.md).
The report is written in English and submitted as PDF, including contribution and
AI usage statements. Tag the completed final version `v1.0` at final delivery.

The report, presentation, and Git history are graded separately. Detailed
presentation requirements have not been supplied yet.

## License

Group-authored scaffold files use the [MIT license](LICENSE). PERIOD retains its
original license in [licenses/PERIOD-MIT.txt](licenses/PERIOD-MIT.txt).

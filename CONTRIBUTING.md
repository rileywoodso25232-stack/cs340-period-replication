# Contributing

## Identity and commits

Every member uses their own GitHub account and an associated Git author email.
Commit subjects follow `STUDENT_ID Full Name: specific change`. Example:

```text
1240013942 刘竞辰: add benchmark selection and logging protocol
```

Include the actual committer's ID and full name on merge/squash commit messages
too. Avoid GitHub's default merge message when it omits these details. Do not
rewrite published history to manufacture progress. AI-assisted work is recorded
in `docs/ai-usage.md`; attribution is not proof of independent contribution.

## Small changes and review

1. Pull the latest `main` before starting work.
2. Create a descriptive task branch, such as `experiments/smoke-run`.
3. Make a substantive change: a script, environment record, protocol, or analysis.
4. Run `python scripts/check_repository.py` and inspect the diff.
5. Push the branch and open a pull request when team review is useful.
6. Review and merge before the weekly check; preserve author attribution.

Before merging, confirm that no one else has changed the same configuration.
Do not commit credentials, images, build artifacts, or files over 50 MB.
The size check is a convenience; it does not replace reviewing file contents.

## Evidence

Record measured data only. Every observation references an original log and an
environment JSON file. Do not count multiple interleavings of the same root cause
as distinct bugs. Freeze selection and parameters before final runs, record failed
or timed-out attempts, and explain exclusions. Store patches for upstream changes.

## Weekly and final delivery

The handout specifies weekly checks each Sunday at 23:59. Confirm the course's
timezone and any first-week clarification with the teaching team. Push before the
deadline; local-only commits do not count. Keep `docs/weekly-log.md` current and
ensure all four members have substantive commits from their own accounts.

At final delivery, verify the clean-machine procedure, English report/PDF,
contribution statement, AI statement, log traceability and final `v1.0` tag.

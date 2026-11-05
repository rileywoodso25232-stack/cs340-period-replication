# AI usage record

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-10-23 | OpenAI Codex | Paper-selection discussion; initial repository layout, documentation and helper scripts | Pending team review; check outputs are recorded separately | No experimental findings were generated |
| 2026-10-27 | OpenAI Codex | Expanded research workflow; local Windows host preflight, WSL prerequisites, pinned source retrieval and a Linux scheduler probe | Pending team review; observed setup states are saved in environment/records/windows-setup/ | No PERIOD build, smoke-test result or research observation has been produced at this stage |

Update this record throughout the project. Record material AI help with code,
analysis and writing, what was checked by humans, and how it was used. Do not claim
human review before it occurs. The final English report includes an AI usage
statement based on this record and the actual contribution history.

## 2026-10-28 更新

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-10-28 | OpenAI Codex | Diagnosed Windows servicing; configured WSL2/LLVM/SVF; executed and archived real bounded smoke runs and replays; organized commit candidates | Team review pending; diagnostics and raw observations retained | Initial environment validation only; no formal replication or Serial comparison |

## 2026-11-05 更新

<!-- reorder3-compat-20261105 -->

| Date | Tool | Assistance | Human verification | Scope limitation |
| --- | --- | --- | --- | --- |
| 2026-11-05 | OpenAI Codex / ChatGPT | Diagnosed IPC layout mismatch; inspected archived ELF DWARF; wrote candidate adaptation, six-run comparison, summary repair and replay helpers; curated evidence and drafted documentation | User executed container commands and backups; six searches completed, both sampled failures replayed with target exit -6; local evidence hashes and repository checks passed; independent team review pending | Single reorder_3 case; candidate Serial correspondence unverified; different period ranges and initialization remain; no speedup or full-paper replication claim |

The initial summary parser missed ANSI-prefixed lines and reported zero schedules. It was corrected using final Round footers without rerunning experiments. Original summaries, logs, correction audit and failed tool attempts were retained in their respective evidence/backup locations.

Same-day scope also includes the earlier Docker reorder_3 search/replay and three native execution batches: ChatGPT assisted with scripts, output interpretation and write-up; the user executed commands and retained evidence. Earlier PERIOD logs remain historical pre-experiments after the IPC mismatch was identified. Final packaging also reviewed the original conversation, preserved failure excerpts, and prepared browser-upload batches; independent team review is still pending.

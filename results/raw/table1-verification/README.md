# PERIOD Table 1 Compatibility Verification

## Date
2026-11-14

## Objective
Verify the observed behavior of three selected benchmark cases
using the local PERIOD replication environment.

## Environment
- Windows, WSL2 and Docker
- Container: period-cs340

## Results
- Selected cases: 3
- Attempted runs: 9
- Completed runs: 9
- Aborted runs: 0
- Timeouts: 0

Detailed measurements are recorded in summary.csv.
Original experimental records are retained in the local backup.

## November 13 original timing for CVE-2016-7911
Wall-clock intervals were calculated from the archived start and end timestamps, which have whole-second precision.

| Original run | Wall-clock interval | Timing treatment |
| --- | ---: | --- |
| 1 | 188 s | Excluded because the interval includes a keypress wait |
| 2 | 6 s | Included |
| 3 | 4 s | Included |

The mean for the two included runs is 5 s. The first run's original timing record and schedule counts are retained. The November 14 verification timings are reported separately in `summary.csv`.

## Limitations
This is a selected-subset verification rather than a complete
replication of Table 1.
Error interleavings do not represent distinct defects.
The exact configuration requires separate verification.
No comparative performance claim is made.

## AI Assistance
ChatGPT assisted with interpreting logs, organizing measurements
and preparing documentation.
The student executed the experimental and verification commands.

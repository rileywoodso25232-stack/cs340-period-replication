# PERIOD Depth-5 Verification

## Date
2026-11-14

## Objective
Evaluate the observed results of PERIOD under the depth-5 configuration.

## Environment
- Windows with WSL2 and Docker
- Existing container: period-cs340
- Depth parameter: 5

## Results
- Total attempted runs: 10
- Completed runs: 9
- Aborted runs: 1
- Timeouts in completed runs: 0

Detailed measurements are recorded in summary.csv.

## Aborted Run
The second run of case 15265 ended with an ASan diagnostic.
The original log was preserved.
Incomplete measurements were excluded from completed-run statistics.

## Data Integrity
All ten original logs were backed up to Windows.
SHA-256 comparisons between Docker and Windows passed.

## Limitations
Error interleavings do not represent distinct defects.
These results alone do not establish the superiority of PERIOD
or constitute a complete replication of the original paper.

## AI Assistance
ChatGPT assisted with log interpretation, data organization,
integrity verification instructions and documentation.
The experiments and verification commands were executed by the student.

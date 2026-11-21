# Serial Driver Compatibility Repairs

## Provenance

Upstream source snapshot:
PERIOD/tool/DBDS/run_OldPDS.py

Original SHA256:
a16575f2480d51496cb3a8387a548efb7ebf04ce2fa6856a0c6785932ee966e1

Compatible candidate:
results/raw/table1-serial-formal-20261121/driver/run_SerialCompat_candidate.py

Candidate SHA256:
30bae09077dbcc9bfa471accb534f4667bc59147a1ed8775d3798535609ab43e

The upstream snapshot was copied from the local
PERIOD Docker container on 2026-11-21.

## Purpose

Adapt the Python driver to the shared-memory ABI
used by the locally compiled benchmark runtime.

## Verified changes

1. SHARE_ARRAY_SIZE: 1990 to 3964.
2. Shared arrays use 16-bit unsigned elements.
3. Validate Sched_Info size: 24008 bytes.
4. Validate offsets: 20, 220, 8148, 16076.
5. Check the existing System V shared-memory segment.
6. Reject unexpected sizes and active attachments.
7. Configure libc function argument and return types.
8. Report shmget/shmat failures using errno.
9. Validate pattern capacity and uint16 value range.
10. Correct shared-memory read/write offsets and sizes.

## Scope of changes

The diff contains four changed sections.

The observed modifications concern shared-memory
layout, access, validation and error handling.

No scheduling-search algorithm changes were
identified in this source comparison.

This observation is not a proof of full behavioral
equivalence with the original paper implementation.

## Experimental evidence

Three selected CVEs were tested at depth 5.

Ten completed Serial runs per CVE,
30 completed runs in total.

Search limit: 10000.
Per-test timeout: 5 seconds.

See:
results/raw/table1-serial-formal-20261121/
results/processed/table1-final/

## Reproducibility limitations

The candidate expects an existing System V
shared-memory segment with key 1111, the expected
layout, and no active attachments.

This setup assumption must be satisfied before
running the compatible driver.

The original repository snapshot is not by itself
proof of the exact version used in the paper.

## Difference record

See serial-compat.diff for the actual source changes.

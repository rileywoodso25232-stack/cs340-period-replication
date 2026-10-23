# Proposed extension: available CPU count

Question: does limiting available cores change PERIOD's detection stability and
wall-clock cost on a fixed, validated subset?

Proposed levels: 2 and 4 available logical CPUs on the same machine. Check that
the chosen input/configuration was not already evaluated in the paper before
describing it as beyond-paper work. If resources do not permit these levels,
revise and justify the design before collecting data.

Hold the program, input, thread count, compiler, detector, search depth, budget,
memory limit and software versions fixed. Pin actual CPU affinity as well as
recording the number of CPUs. Treat this as a separate campaign from replication.
Run each condition at least three times. Collect detection, schedule metrics,
runtime, timeouts and replay evidence. Do not classify a timeout as a bug without
verification.

Interpret whether findings concern search behavior, execution overhead, or
resource sensitivity; do not infer universal scaling from two core counts.
If another factor must change, record the deviation or redesign the experiment.

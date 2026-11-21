import csv
import json
import resource
import subprocess
import time
from pathlib import Path

resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
root = Path.cwd()
session = root / ("native-batches-" + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))
session.mkdir()
config = dict(groups=3, max_executions=1000, execution_timeout_seconds=5,
              group_timeout_seconds=120, arguments=[],
              oracle="Bug found! plus assertion failure diagnostic")
(session / "config.json").write_text(json.dumps(config, indent=2))

for group in range(1, 4):
    folder = session / ("group-%d" % group)
    folder.mkdir()
    start = time.monotonic()
    counts = dict(assertion=0, normal=0, timeout=0, other_error=0)
    first_bug = None
    with (folder / "executions.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["execution", "returncode", "outcome", "wall_seconds"])
        for index in range(1, 1001):
            remaining = 120 - (time.monotonic() - start)
            if remaining <= 0:
                break
            tick = time.monotonic()
            try:
                p = subprocess.run(
                    [str(root / "reorder_3_native")],
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    timeout=min(5, remaining))
                output = p.stdout
                code = p.returncode
                if b"Bug found!" in output and b"Assertion" in output:
                    outcome = "assertion"
                    if first_bug is None:
                        first_bug = index
                elif code == 0:
                    outcome = "normal"
                else:
                    outcome = "other_error"
            except subprocess.TimeoutExpired as e:
                output = e.output or b""
                code = None
                outcome = "timeout"
            if output:
                (folder / ("%04d.log" % index)).write_bytes(output)
            counts[outcome] += 1
            writer.writerow([index, code, outcome, time.monotonic() - tick])
            f.flush()
    result = dict(group=group, executions=sum(counts.values()),
                  outcomes=counts, first_bug_execution=first_bug,
                  wall_seconds=time.monotonic() - start)
    (folder / "summary.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result), flush=True)
print("Saved:", session)

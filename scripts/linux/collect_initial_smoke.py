"""Collect the initial bounded validation runs; exclude executable binaries."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import statistics
import sys

repo = Path(sys.argv[1])
destination = repo / 'results/raw/local-smoke-20261028'
destination.mkdir(parents=True, exist_ok=True)
rows = []
for run in sorted(Path('/root/cs340-period/smoke').iterdir()):
    if not run.is_dir() or not (run / 'search.log').exists():
        continue
    target = destination / run.name
    target.mkdir(exist_ok=True)
    for source in run.rglob('*'):
        if source.is_file() and source.name not in ('df', 'reorder_3_bad'):
            output = target / source.relative_to(run)
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(source), str(output))
    log = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'search.log').read_text())
    elapsed = re.search(r'Time\s+\S+\s+(\d+):(\d+):(\d+\.\d+)', log)
    errors = re.search(r'Total Error Interleavings:\s*(\d+)', log)
    timeouts = re.search(r'Total Timeouts Interleavings:\s*(\d+)', log)
    rounds = re.search(r'Round\s+\d+\s+(\d+)', log)
    binary = run / ('df' if 'doublefree' in run.name else 'reorder_3_bad')
    rows.append(dict(run=run.name, exit_code=int((run/'search.exit').read_text()),
                     schedules=int(rounds[1]) if rounds else None,
                     error_schedules=int(errors[1]) if errors else None,
                     timeouts=int(timeouts[1]) if timeouts else None,
                     tool_seconds=sum(float(v)*m for v,m in zip(elapsed.groups(),[3600,60,1])) if elapsed else None,
                     executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                     replay_exit=int((run/'replay.exit').read_text()) if (run/'replay.exit').exists() else None))
times=[r['tool_seconds'] for r in rows if r['run'].startswith('reorder3-') and r['tool_seconds'] is not None]
report=dict(kind='environment_validation_not_formal_results', source_commit='cb8deb9a176e5bb292d70d46557dd61dc0e98069',
            linux_directory_timestamps='UTC; user-facing timezone Asia/Shanghai',
            search_depth=3, reorder_schedule_limit=1000, outer_timeout_seconds=120,
            replay_timeout_seconds=60, per_execution_timeout_seconds=5,
            runs=rows, reorder_mean_seconds=statistics.mean(times), reorder_sample_sd_seconds=statistics.stdev(times))
(destination/'summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))

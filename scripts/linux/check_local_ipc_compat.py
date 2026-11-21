#!/usr/bin/env python3
"""Read-only ABI evidence and patch applicability check (Python 3.6+).

Does not import a driver, run a target, attach IPC, or apply a patch.
"""
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

root = Path('/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069')
repo = Path(__file__).resolve().parents[2]
target = root / 'evaluation/CS/reorder_3/reorder_3_bad'
dump = subprocess.check_output(['readelf', '--debug-dump=info', str(target)]).decode('utf-8')
lines = dump.splitlines()
index = next(i for i, line in enumerate(lines) if re.search(r'DW_AT_name.*: Sched_Info$', line))
evidence = '\n'.join(lines[index - 2:index + 100])
checks = {}
for mode, name in [('period', 'run_PDS.py'), ('serial', 'run_OldPDS.py')]:
    source = root / 'tool/DBDS' / name
    patch = repo / 'src/patches/teammate-ipc-compat' / (mode + '.diff')
    result = subprocess.run(['patch', '--dry-run', '--batch', str(source)],
                            input=patch.read_bytes(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    checks[mode] = {'source': str(source), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                    'array_capacity': re.search(r'^SHARE_ARRAY_SIZE\s*=\s*(\d+)', source.read_text(encoding='utf-8'), re.M).group(1),
                    'patch_dry_run_exit': result.returncode,
                    'patch_dry_run_output': result.stdout.decode('utf-8', errors='replace')}
print(json.dumps({'kind': 'read-only compatibility evidence; no dynamic validation',
                  'kernel': platform.release(), 'target': str(target),
                  'target_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                  'dwarf_excerpt': evidence,
                  'ipc_snapshot': Path('/proc/sysvipc/shm').read_text(),
                  'drivers': checks}, ensure_ascii=True, indent=2))


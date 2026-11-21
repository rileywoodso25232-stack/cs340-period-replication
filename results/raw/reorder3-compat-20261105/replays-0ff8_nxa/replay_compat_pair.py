#!/usr/bin/env python3
"""Replay one saved failure per candidate, with separate evidence and target exit codes."""
import importlib.util
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile

RUNNER = '''import json, runpy, subprocess, sys
from pathlib import Path
original = subprocess.Popen
class Traced(original):
    def communicate(self, *args, **kwargs):
        result = super().communicate(*args, **kwargs)
        with open('target-exits.jsonl', 'a') as record:
            record.write(json.dumps({'command': self.args, 'returncode': self.returncode}, default=str) + '\\n')
        return result
subprocess.Popen = Traced
driver = sys.argv[1]
sys.path.insert(0, str(Path(driver).parent))
sys.argv = [driver, '-y', '-t', '5', '-r', './failure.schedule', './reorder_3_bad']
runpy.run_path(driver, run_name='__main__')
'''


def main():
    root = Path(sys.argv[1]).resolve()
    spec = importlib.util.spec_from_file_location('helper', str(root / 'prepare_serial_compat.py'))
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    output = Path(tempfile.mkdtemp(prefix='replays-', dir=str(root)))
    shutil.copy2(str(Path(__file__).resolve()), str(output / Path(__file__).name))
    print('Replay evidence directory: ' + str(output), flush=True)
    all_ok = True
    def no_core():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    for method in ('serial', 'period'):
        source = root / method / 'group-1'
        errors = sorted(source.glob('out_reorder_3_bad_*/Errors/*assertion-failed'))
        if not errors:
            raise RuntimeError('No saved assertion failure for ' + method)
        if helper.digest(source / 'reorder_3_bad') != helper.VERIFIED_BINARY_SHA256:
            raise RuntimeError('Binary hash mismatch')
        helper.ipc_idle_preflight()
        folder = output / method
        folder.mkdir()
        for name in ('reorder_3_bad', 'ConConfig.reorder_3_bad', 'mempair.reorder_3_bad.npz'):
            shutil.copy2(str(source / name), str(folder / name))
        shutil.copy2(str(errors[0]), str(folder / 'failure.schedule'))
        (folder / 'runner.py').write_text(RUNNER, encoding='utf-8')
        command = ['timeout', '--kill-after=5s', '30s', sys.executable, '-u', '-X', 'faulthandler',
                   str(folder / 'runner.py'), str(root / method / 'driver/run_candidate.py')]
        (folder / 'command.json').write_text(json.dumps(command, indent=2), encoding='utf-8')
        with (folder / 'replay.log').open('wb') as log:
            proc = subprocess.run(command, cwd=str(folder), stdout=log,
                                  stderr=subprocess.STDOUT, preexec_fn=no_core)
        (folder / 'driver.exit').write_text(str(proc.returncode) + '\n', encoding='ascii')
        log_text = (folder / 'replay.log').read_text(encoding='utf-8', errors='replace')
        exits_path = folder / 'target-exits.jsonl'
        exits = [json.loads(line) for line in exits_path.read_text().splitlines()] if exits_path.exists() else []
        target_exit = exits[-1]['returncode'] if len(exits) >= 2 else None
        ok = (proc.returncode == 0 and target_exit == -6 and
              'Perform Reproduction!' in log_text and 'Assertion' in log_text and 'failed' in log_text)
        result = {'method': method, 'saved_failure': str(errors[0].relative_to(root)),
                  'driver_exit': proc.returncode, 'replay_target_exit': target_exit,
                  'assertion_reproduced': ok}
        (folder / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result), flush=True)
        print(log_text, flush=True)
        all_ok = all_ok and ok
        if proc.returncode in (124, 137):
            print('Timed out; stopped without retry. Inspect remaining processes before further experiments.')
            break
    files = [p for p in output.rglob('*') if p.is_file()]
    (output / 'hashes.sha256').write_text(''.join(helper.digest(p) + '  ' + str(p.relative_to(output)) + '\n'
        for p in sorted(files)), encoding='utf-8')
    print('Replay evidence directory: ' + str(output))
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())

import json, runpy, subprocess, sys
from pathlib import Path
original = subprocess.Popen
class Traced(original):
    def communicate(self, *args, **kwargs):
        result = super().communicate(*args, **kwargs)
        with open('target-exits.jsonl', 'a') as record:
            record.write(json.dumps({'command': self.args, 'returncode': self.returncode}, default=str) + '\n')
        return result
subprocess.Popen = Traced
driver = sys.argv[1]
sys.path.insert(0, str(Path(driver).parent))
sys.argv = [driver, '-y', '-t', '5', '-r', './failure.schedule', './reorder_3_bad']
runpy.run_path(driver, run_name='__main__')

import json, os, runpy, subprocess, sys
original_popen = subprocess.Popen
class ObservedPopen(original_popen):
    def communicate(self, *args, **kwargs):
        try:
            return super().communicate(*args, **kwargs)
        finally:
            if self.returncode is not None and not getattr(self, '_recorded', False):
                with open(os.environ['CS340_TARGET_EXITS'], 'a', encoding='utf-8') as log:
                    log.write(json.dumps({'pid': self.pid, 'args': self.args, 'returncode': self.returncode}) + '\n')
                self._recorded = True
subprocess.Popen = ObservedPopen
driver = sys.argv[1]
sys.argv = sys.argv[1:]
sys.path.insert(0, os.path.dirname(driver))
runpy.run_path(driver, run_name='__main__')

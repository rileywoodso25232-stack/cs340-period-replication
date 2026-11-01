"""Check SCHED_DEADLINE on this process, restore SCHED_OTHER, and report JSON.

Run inside the intended Linux environment as root. This is a kernel/permission
probe, not a PERIOD experiment. No global scheduler setting is changed.
"""

import ctypes
import errno
import json
import os
import platform
import sys


class SchedAttr(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_uint32),
        ("policy", ctypes.c_uint32),
        ("flags", ctypes.c_uint64),
        ("nice", ctypes.c_int32),
        ("priority", ctypes.c_uint32),
        ("runtime", ctypes.c_uint64),
        ("deadline", ctypes.c_uint64),
        ("period", ctypes.c_uint64),
    ]


def main():
    result = {
        "system": platform.system(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "deadline_probe_passed": False,
        "period_smoke_test_run": False,
    }
    if sys.platform != "linux":
        result["status"] = "requires_linux"
        print(json.dumps(result, indent=2))
        return 2
    syscall_numbers = {"x86_64": 314, "aarch64": 274}
    number = syscall_numbers.get(platform.machine())
    if number is None:
        result["status"] = "unsupported_probe_architecture"
        print(json.dumps(result, indent=2))
        return 2
    result["effective_uid"] = os.geteuid()
    result["cpu_affinity"] = sorted(os.sched_getaffinity(0))
    result["initial_policy"] = os.sched_getscheduler(0)
    if result["initial_policy"] != os.SCHED_OTHER:
        result["status"] = "requires_initial_sched_other"
        print(json.dumps(result, indent=2))
        return 2
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    attr = SchedAttr()
    attr.size = ctypes.sizeof(SchedAttr)
    attr.policy = 6  # Linux SCHED_DEADLINE
    attr.runtime = 1_000_000  # 1 ms, 1% reservation per 100 ms period
    attr.deadline = 100_000_000
    attr.period = 100_000_000
    changed = False
    try:
        rc = libc.syscall(ctypes.c_long(number), ctypes.c_int(0), ctypes.byref(attr), ctypes.c_uint(0))
        if rc != 0:
            error = ctypes.get_errno()
            result.update(status="sched_setattr_failed", errno=error,
                          errno_name=errno.errorcode.get(error), error=os.strerror(error))
        else:
            changed = True
            result["observed_policy"] = os.sched_getscheduler(0)
            result["status"] = "policy_observed" if result["observed_policy"] == 6 else "unexpected_policy"
    finally:
        if changed:
            try:
                os.sched_setscheduler(0, os.SCHED_OTHER, os.sched_param(0))
                result["restored_policy"] = os.sched_getscheduler(0)
                result["deadline_probe_passed"] = (
                    result.get("observed_policy") == 6 and result["restored_policy"] == os.SCHED_OTHER
                )
                if result["deadline_probe_passed"]:
                    result["status"] = "passed_and_restored"
            except OSError as error:
                result.update(status="restore_failed", restore_error=str(error))
    print(json.dumps(result, indent=2))
    return 0 if result["deadline_probe_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())

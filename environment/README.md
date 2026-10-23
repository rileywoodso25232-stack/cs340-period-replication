# Environment setup (not yet validated)

## Original artifact

Start with the pinned implementation's `INSTALL.md` and `REQUIREMENTS.md` after
running `python scripts/fetch_upstream.py`. The author's Dockerfile uses Ubuntu
18.04. The paper reports GCC 7.5 and LLVM 10.0. These are original reference
settings, not a statement that they are installed on a group machine.

The original installation guide recommends a multi-core Linux host with kernel
4.x or newer and runs the artifact container with privileged access. Validate
this route on a dedicated experiment machine or VM before adopting it.

## Initial procedure to validate

```sh
python3 scripts/fetch_upstream.py
cd third_party/PERIOD
docker build -t cs340-period:setup .
docker run --privileged -it cs340-period:setup /bin/bash
```

These are the upstream build route adapted to the group checkout; they have not
been exercised for this project. Historical package sources or downloads may need
repair. Record each change as a patch and deviation rather than silently replacing
compiler versions. Do not change unrelated settings during debugging.

Inside the configured container, inspect the setup and run the smoke procedure.
Record exact working directories and export/copy original logs into this group
repository. The container is not yet configured to export logs automatically.

## Required records

Run `python3 scripts/capture_environment.py` on the machine used for each campaign.
For a container, record both host and container environments. Also record:

- CPU model, physical/logical cores, RAM, CPU affinity and background workloads.
- OS release, host/guest kernel, architecture and virtualization mode.
- Git, GCC, Clang/LLVM, Python and dependency versions, compile flags and oracle.
- Docker version, image ID/digest, mounted paths and CPU/memory limits.
- Upstream SHA, group commit, actual modifications and workload hashes.
- Commands, measured build/runtime, failures and reproduction steps.

The capture helper collects a subset automatically. Fill missing fields from
actual observations. Final reproducibility requires pinning all acquired inputs
and dependencies, not just the upstream SHA. Add a validated setup script or
Dockerfile here after a successful smoke test.

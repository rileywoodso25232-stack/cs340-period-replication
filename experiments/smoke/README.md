# Installation smoke test

Status: planned; not executed. Run inside the configured upstream Linux environment.

The pinned upstream checkout provides `test/doubleFree/`. From its root:

```sh
source tool/init_env.sh
cd test/doubleFree
./cleanDIR.sh
./build.sh
"$ROOT_DIR/tool/DBDS/run_PDS.py" -y -d 3 ./df
```

The upstream README illustrates six tested schedules and four failing schedules
at depth three for this example. That is an installation reference, not a result
produced by this group. Several failing schedules can represent one bug.

Save stdout/stderr, exit status, the command, environment, and generated schedules.
Replay a saved failing schedule with upstream `run_PDS.py -r <saved-file> ./df`.
Copy small cited logs into `results/raw/`; keep bulk output out of Git.
Record differences or installation failures before attempting final benchmarks.

Next gate: validate at least one `evaluation/` subject and the intended baseline,
then freeze the actual main-experiment configuration. Smoke success alone does
not establish the paper's research claims.

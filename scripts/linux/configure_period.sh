#!/bin/bash
# Run after OS dependencies and LLVM 10 extraction. Logs stay on Linux.
set -euo pipefail
export ROOT_DIR=/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069
export PATH="$ROOT_DIR/clang+llvm/bin:$ROOT_DIR/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$ROOT_DIR/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LLVM_DIR="$ROOT_DIR/clang+llvm/lib/cmake/llvm"
export LLVM_COMPILER=clang
export CC=clang CXX=clang++
logs=/root/cs340-period/setup-logs
mkdir -p "$logs"
trap 'echo "failed at line $LINENO" > "$logs/status"' ERR
echo python_dependencies > "$logs/status"
DEBIAN_FRONTEND=noninteractive apt-get -y install python-numpy python3-numpy python3-sysv-ipc > "$logs/python-deps.log" 2>&1
python -c 'import numpy; print(numpy.__version__)'
python3 -c 'import numpy, sysv_ipc; print(numpy.__version__, sysv_ipc.__version__)'
pip install --no-deps -e "$ROOT_DIR/tool/wllvm" > "$logs/wllvm.log" 2>&1
echo svf_configure > "$logs/status"
mkdir -p "$ROOT_DIR/tool/SVF/Release-build"
cd "$ROOT_DIR/tool/SVF/Release-build"
cmake -DLLVM_DIR="$LLVM_DIR" .. > "$logs/svf-cmake.log" 2>&1
echo svf_build > "$logs/status"
make -j4 > "$logs/svf-build.log" 2>&1
./bin/wpa --version > "$logs/wpa-version.log" 2>&1
echo static_analysis > "$logs/status"
cd "$ROOT_DIR/tool/staticAnalysis/LLVM-PASS"
cmake -DLLVM_DIR="$LLVM_DIR" . > "$logs/pass-cmake.log" 2>&1
make -j4 > "$logs/pass-build.log" 2>&1
echo instrumentation > "$logs/status"
cd "$ROOT_DIR/tool/staticAnalysis/DBDS-INSTRU/llvm-mode"
make -j4 > "$logs/instrumentation-build.log" 2>&1
echo completed > "$logs/status"

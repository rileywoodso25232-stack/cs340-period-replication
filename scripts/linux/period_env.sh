# Source this file in bash inside CS340-PERIOD.
export ROOT_DIR=/root/cs340-period/source/cb8deb9a176e5bb292d70d46557dd61dc0e98069
export PATH="$ROOT_DIR/clang+llvm/bin:$ROOT_DIR/tool/SVF/Release-build/bin:$PATH"
export LD_LIBRARY_PATH="$ROOT_DIR/clang+llvm/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export LLVM_DIR="$ROOT_DIR/clang+llvm/lib/cmake/llvm"
export LLVM_COMPILER=clang

#!/usr/bin/env bash
# Local build (Linux, macOS or Git Bash on Windows) once deps-install/ exists
# (from scripts/build-deps.sh or the "Dependencies" workflow artifact).
#   EMSDK=/path/to/emsdk BAMBU_TAG=v02.09.01.70 bash scripts/local-build.sh [configure|build|all]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source "$EMSDK/emsdk_env.sh" >/dev/null 2>&1
STEP="${1:-all}"
TAG="${BAMBU_TAG:-v02.09.01.70}"
R="$ROOT"; command -v cygpath >/dev/null && R="$(cygpath -m "$ROOT")"
D="$R/deps-install"

if [[ "$STEP" == all || "$STEP" == source ]]; then
  if [[ ! -d bambu ]]; then
    git clone -q --depth 1 --branch "$TAG" --filter=blob:none --sparse https://github.com/bambulab/BambuStudio.git bambu
    git -C bambu sparse-checkout set src cmake deps
  fi
  python3 tools/prepare.py bambu || python tools/prepare.py bambu
fi

if [[ "$STEP" == all || "$STEP" == configure ]]; then
  emcmake cmake -S bambu -B build-wasm -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH="$D" -DCMAKE_MODULE_PATH="$R/cmake" \
    -DCMAKE_PROJECT_INCLUDE_BEFORE="$R/cmake/wasm_find_paths.cmake" -DBAMBU_WASM_DIR="$R" \
    -DSLIC3R_GUI=OFF -DSLIC3R_STATIC=ON -DSLIC3R_PCH=ON \
    -DSLIC3R_ENABLE_OPENMESHCRAFT_BOOLEAN=OFF -DSLIC3R_ALLOW_MCUT_BOOLEAN=ON \
    -DBOOST_ROOT="$D" -DBoost_ROOT="$D" -DCGAL_DIR="$D/lib/cmake/CGAL" \
    -DNLOPT_LIBRARY="$D/lib/libnlopt.a" -DNLOPT_INCLUDE_DIR="$D/include" \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DBBL_RELEASE_TO_PUBLIC=1 \
    "-DCMAKE_CXX_FLAGS=-I$R/shim-common -fwasm-exceptions -pthread" \
    "-DCMAKE_C_FLAGS=-sSUPPORT_LONGJMP=wasm -pthread"
fi

if [[ "$STEP" == all || "$STEP" == build ]]; then
  cmake --build build-wasm --target BambuStudio -- -k 0
fi

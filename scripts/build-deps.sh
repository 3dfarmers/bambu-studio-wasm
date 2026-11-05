#!/usr/bin/env bash
# Build the WebAssembly dependencies of Bambu Studio's slicing core into deps-install/.
#
# Slim on purpose: only what loading a Bambu Studio project, slicing it and writing
# the G-code needs. Not built (stubbed in the engine instead): OCCT (STEP import),
# OpenCV (texture colours), Assimp (OBJ/glTF import), Freetype (text), OpenVDB
# (SLA hollowing), OpenMeshCraft (GUI mesh booleans), curl/OpenSSL, OpenGL/GLFW/wx.
#
# Needs: emsdk activated or EMSDK set, cmake, ninja, python3, m4, curl, a host clang
# (Boost's b2 bootstrap). Each library writes a stamp file, so a rerun only builds
# what is missing. Adapted from OrcaWasm (github.com/Hiosdra/OrcaWeb, AGPL-3.0).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INSTALL="${DEPS_INSTALL:-$ROOT/deps-install}"
WORK="${DEPS_WORK:-/tmp/bsw-deps}"
JOBS="${JOBS:-$(nproc)}"
# CMake 4 refuses projects that ask for a minimum below 3.5 (Expat, NLopt, libnoise).
export CMAKE_POLICY_VERSION_MINIMUM=3.5
CXXF="-fwasm-exceptions -pthread"
CF="-sSUPPORT_LONGJMP=wasm -pthread"
mkdir -p "$INSTALL" "$WORK"
# shellcheck disable=SC1091
source "$EMSDK/emsdk_env.sh" >/dev/null 2>&1

have() { [[ -f "$INSTALL/.stamp-$1" ]]; }
mark() { touch "$INSTALL/.stamp-$1"; echo "[deps] $1 done"; }
fetch() { curl -fL --retry 3 "$1"; }

# ---- Boost 1.84 (the version Bambu Studio 2.09 pins) ------------------------
# Bambu builds Boost.Log with threads (no BOOST_LOG_NO_THREADS), so the
# multithreaded v2_mt ABI is what libslic3r expects.
if ! have boost-1.84.0-v1; then
  rm -rf "$WORK/boost_1_84_0"
  fetch https://archives.boost.org/release/1.84.0/source/boost_1_84_0.tar.gz | tar xz -C "$WORK"
  cd "$WORK/boost_1_84_0"
  ./bootstrap.sh --with-toolset=clang
  printf "using clang : emscripten : em++ :\n<archiver>emar\n<ranlib>emranlib ;\n" > "$HOME/user-config.jam"
  ./b2 toolset=clang-emscripten variant=release link=static threading=multi \
    --layout=system --prefix="$INSTALL" \
    --with-atomic --with-chrono --with-date_time --with-filesystem --with-iostreams \
    --with-locale --with-log --with-nowide --with-regex --with-system --with-thread \
    define=BOOST_LOG_WITHOUT_SYSLOG=1 boost.locale.icu=off \
    "cxxflags=$CXXF" -j"$JOBS" install
  cd "$ROOT"
  mark boost-1.84.0-v1
fi

# ---- GMP / MPFR / CGAL (CGAL is used by Arachne walls and mesh tools) -------
if ! have math-v1; then
  fetch https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz | tar xJ -C "$WORK"
  cd "$WORK/gmp-6.3.0"
  printf 'gmp_cv_asm_label_suffix=":"\n' > "$WORK/gmp_site.sh"
  export gmp_cv_asm_label_suffix=":"
  CFLAGS="$CF" CXXFLAGS="$CXXF" CONFIG_SITE="$WORK/gmp_site.sh" emconfigure ./configure \
    --prefix="$INSTALL" --host=wasm32-unknown-emscripten \
    --disable-shared --enable-static --disable-assembly --enable-cxx
  emmake make -j"$JOBS" && make install
  fetch https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.xz | tar xJ -C "$WORK"
  cd "$WORK/mpfr-4.2.1"
  CFLAGS="$CF" CXXFLAGS="$CXXF" emconfigure ./configure \
    --prefix="$INSTALL" --with-gmp="$INSTALL" --disable-shared --enable-static
  emmake make -j"$JOBS" && make install
  fetch https://github.com/CGAL/cgal/releases/download/v5.6.2/CGAL-5.6.2.tar.xz | tar xJ -C "$WORK"
  cmake -S "$WORK/CGAL-5.6.2" -B "$WORK/cgal-build" -G Ninja \
    -DCMAKE_INSTALL_PREFIX="$INSTALL" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$WORK/cgal-build" --target install
  cd "$ROOT"
  mark math-v1
fi

# ---- EXPAT / NLopt / cereal ---------------------------------------------------
if ! have small-v1; then
  fetch https://github.com/libexpat/libexpat/releases/download/R_2_5_0/expat-2.5.0.tar.xz | tar xJ -C "$WORK"
  emcmake cmake -S "$WORK/expat-2.5.0" -B "$WORK/expat-build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL" -DEXPAT_BUILD_TOOLS=OFF -DEXPAT_BUILD_EXAMPLES=OFF \
    -DEXPAT_BUILD_TESTS=OFF -DEXPAT_SHARED_LIBS=OFF -DEXPAT_BUILD_DOCS=OFF "-DCMAKE_C_FLAGS=$CF"
  cmake --build "$WORK/expat-build" --target install
  fetch https://github.com/stevengj/nlopt/archive/v2.7.1.tar.gz | tar xz -C "$WORK"
  emcmake cmake -S "$WORK/nlopt-2.7.1" -B "$WORK/nlopt-build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL" -DNLOPT_CXX=ON -DNLOPT_PYTHON=OFF -DNLOPT_GUILE=OFF \
    -DNLOPT_MATLAB=OFF -DNLOPT_OCTAVE=OFF -DNLOPT_SWIG=OFF -DNLOPT_TESTS=OFF -DBUILD_SHARED_LIBS=OFF \
    "-DCMAKE_C_FLAGS=$CF" "-DCMAKE_CXX_FLAGS=$CXXF"
  cmake --build "$WORK/nlopt-build" --target install
  git clone -q --depth 1 --branch v1.3.2 https://github.com/USCiLab/cereal.git "$WORK/cereal"
  cmake -S "$WORK/cereal" -B "$WORK/cereal-build" -G Ninja -DCMAKE_INSTALL_PREFIX="$INSTALL" \
    -DJUST_INSTALL_CEREAL=ON -DSKIP_PERFORMANCE_COMPARISON=ON -DBUILD_SANDBOX=OFF -DBUILD_DOC=OFF
  cmake --build "$WORK/cereal-build" --target install
  mark small-v1
fi

# ---- libnoise (Bambu's fork; fuzzy skin) -------------------------------------
if ! have libnoise-1.0.0-v1; then
  rm -rf "$WORK/libnoise-1.0.0"
  fetch https://github.com/bambulab/libnoise/archive/refs/tags/v1.0.0.tar.gz | tar xz -C "$WORK"
  emcmake cmake -S "$WORK/libnoise-1.0.0" -B "$WORK/libnoise-build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL" -DCMAKE_POLICY_VERSION_MINIMUM=3.5 "-DCMAKE_DEBUG_POSTFIX:STRING=" \
    "-DCMAKE_CXX_FLAGS=$CXXF" "-DCMAKE_C_FLAGS=$CF"
  cmake --build "$WORK/libnoise-build" --target install
  mark libnoise-1.0.0-v1
fi

# ---- oneTBB (2021.13 has Emscripten support; API matches Bambu's 2021.5) -----
if ! have onetbb-2021.13.2-v1; then
  rm -rf "$WORK/onetbb"
  git clone -q --depth 1 --branch v2021.13.2 https://github.com/uxlfoundation/oneTBB.git "$WORK/onetbb"
  cmake -DTBB_SOURCE_DIR="$WORK/onetbb" -P "$ROOT/patches/onetbb/wasm-exceptions.cmake"
  emcmake cmake -S "$WORK/onetbb" -B "$WORK/onetbb-build" -G Ninja -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL" "-DCMAKE_C_FLAGS=$CF" "-DCMAKE_CXX_FLAGS=$CXXF" \
    -DBUILD_SHARED_LIBS=OFF -DTBB_TEST=OFF -DTBB_EXAMPLES=OFF -DTBB_STRICT=OFF \
    -DTBB_DISABLE_HWLOC_AUTOMATIC_SEARCH=ON
  cmake --build "$WORK/onetbb-build" --target install
  mark onetbb-2021.13.2-v1
fi

echo "[deps] all done in $INSTALL"
ls "$INSTALL/lib"

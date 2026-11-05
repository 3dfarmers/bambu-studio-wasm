# Notices

This repository builds third-party software. Each part keeps its own license.

- **Bambu Studio** — Copyright (C) Bambu Lab, and the PrusaSlicer and Slic3r authors it
  is based on. AGPL-3.0. https://github.com/bambulab/BambuStudio
- **OrcaWasm** — Copyright (C) its contributors. AGPL-3.0.
  https://github.com/Hiosdra/OrcaWeb. `scripts/prepare-emscripten-eh.py`,
  `patches/onetbb/wasm-exceptions.cmake` and parts of `scripts/build-deps.sh` are taken
  from or based on it.
- Libraries built by `scripts/build-deps.sh`, under their own licenses: Boost (BSL-1.0),
  GMP and MPFR (LGPL-3.0), CGAL (GPL-3.0 / LGPL-3.0), Expat (MIT), NLopt (MIT / LGPL),
  cereal (BSD-3-Clause), libnoise (LGPL-2.1), oneTBB (Apache-2.0), zlib, libpng and
  libjpeg (their own permissive licenses).

Changes made here are released under AGPL-3.0.

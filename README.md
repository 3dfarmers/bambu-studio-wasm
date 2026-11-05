# bambu-studio-wasm

Bambu Studio's slicer compiled to WebAssembly, so a web page can slice a Bambu Studio
project on the visitor's own computer, with no server involved.

[3D Farmers](https://3d-farmers.com) uses it in FarmLoop's print tuning: the page slices
the original project and its tuned versions in the browser to show real print times
and to offer ready-to-print files.

**Status: experimental (spike done 2026-11-05).**

## What is in it

- Bambu Studio's command-line slicer (`src/BambuStudio.cpp`) and its slicing core
  `libslic3r`, from [Bambu Studio](https://github.com/bambulab/BambuStudio)
  `v02.09.01.70`, compiled unchanged apart from a few build patches
  (`tools/prepare.py`).
- The CLI needs Bambu's plate code (`PartPlate`), which lives in the desktop GUI.
  `tools/prepare.py` takes Bambu's own `PartPlate.cpp` and stubs only its drawing
  functions (the list is written to `wasm-gen/stubbed-functions.txt`); `shim/` has
  placeholder headers for the GUI types it mentions. No window, no OpenGL.
- Left out on purpose, to keep it small: STEP import (OpenCASCADE), textured OBJ/glTF
  import (Assimp, OpenCV), text shapes (Freetype), SLA hollowing (OpenVDB), encrypted
  log upload (OpenSSL, HTTP), thumbnail rendering. `overrides/libslic3r/wasm_stubs.cpp`
  has the few stand-ins the linker asks for.

## Measured (hopper, 4.5 h print, Bambu Studio 2.09, 16-thread PC)

| | Desktop CLI 2.09 | This engine (Chrome) |
|---|---|---|
| Original | 4:31:09 | 4:30:32 (−0.23 %) |
| Quality | 4:01:37 | 4:00:37 (−0.42 %) |
| Quality + speed | 3:39:44 | 3:38:43 (−0.46 %) |
| Speed | 3:35:03 | 3:34:29 (−0.27 %) |
| Filament | 146.97 g | 146.97 g |
| Slice time | ~10 s | 10–14 s |

The G-code first differs by 0.001 mm in a coordinate (floating-point maths library),
which later changes a few path-ordering decisions; per-feature times for walls,
bridges and surfaces are identical.

Download: `bambu-slicer.wasm` 13.9 MB (3.1 MB brotli), Bambu printer profiles 7.1 MB
(0.14 MB brotli). Memory: about 1.3 GB for this part (wasm32 limit: 4 GB).

## Using it

The page needs cross-origin isolation for threads (`Cross-Origin-Opener-Policy:
same-origin` and `Cross-Origin-Embedder-Policy: require-corp` or `credentialless`).

```js
const mod = await BambuSlicer({ mainScriptUrlOrBlob: "/bambu-slicer.js" });
// printer profiles -> /bambu/resources/profiles/..., project -> /in/p.3mf
mod.callMain(["--slice", "1", "--allow-newer-file=1", "--outputdir", "/out",
              "--export-3mf", "o.gcode.3mf", "/in/p.3mf"]);
// Finished when /out/result.json exists (it carries the return code and the times).
// Like the desktop CLI, the engine does not shut down on its own: drop the worker.
```

`test/slice-node.mjs` does the same in Node; `test/browser.html` + `test/serve.mjs`
in a browser.

## Build

1. Dependencies: `.github/workflows/deps.yml` on GitHub, or
   `EMSDK=/path/to/emsdk bash scripts/build-deps.sh` (Linux/macOS).
2. Engine: `.github/workflows/engine.yml`, or
   `EMSDK=/path/to/emsdk bash scripts/local-build.sh` (also works in Git Bash on
   Windows once `deps-install/` exists).

Emscripten 3.1.74, CMake, Ninja, Python 3.

## License

AGPL-3.0, like Bambu Studio. See `LICENSE` and `NOTICE.md`. If you received this
engine as part of a web page, this repository is its complete corresponding source.

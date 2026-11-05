# bambu-studio-wasm

Bambu Studio's slicing core compiled to WebAssembly, so a web page can slice a
Bambu Studio project on the visitor's own computer, with no server involved.

[3D Farmers](https://3d-farmers.com) uses it in FarmLoop's print tuning: the page slices
the original project and its tuned versions in the browser to show real print times
and to offer ready-to-print files.

**Status: experimental.** The first goal is the same print time as the Bambu Studio
desktop slicer for the same project.

## What is in it

- `libslic3r` from [Bambu Studio](https://github.com/bambulab/BambuStudio)
  (currently `v02.09.01.70`), unchanged except for the build patches in `patches/`.
- A small command-line driver (`driver/`): load a `.3mf` project, slice one plate,
  write the G-code, a sliced `.gcode.3mf` and the slicer's time and filament
  statistics. Bambu Studio's own CLI needs its GUI classes (plates, thumbnails), so
  it is not compiled here; the driver uses the same slicing calls.
- Left out on purpose to keep it small: STEP/OBJ/glTF import, text, textures,
  SLA, arranging, thumbnails rendering, network code.

## Build

The dependencies build on GitHub Actions (`.github/workflows/deps.yml`) or locally:

```bash
EMSDK=/path/to/emsdk bash scripts/build-deps.sh
```

Emscripten 3.1.74, CMake, Ninja, Python 3, m4 and a host clang are needed.

## License

AGPL-3.0, like Bambu Studio. See `LICENSE` and `NOTICE.md`. If you received this
engine as part of a web page, this repository is its complete corresponding source.

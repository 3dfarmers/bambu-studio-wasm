#!/usr/bin/env python3
"""Prepare a Bambu Studio checkout for the WebAssembly build.

    python3 tools/prepare.py <bambu-studio-checkout>

What it does (idempotent: run it on a fresh checkout):
1. Generates `wasm-gen/slic3r/GUI/` inside the checkout: Bambu's own PartPlate.hpp,
   PartPlate.cpp with every drawing/GUI-only function reduced to an empty stub, the
   wipe tower placement code unchanged, BitmapCache's colour parser and Plater's
   get_min_flush_volumes(). Placeholder headers from `shim/` sit next to them.
2. Moves `src/slic3r` (the desktop GUI) out of the way so nothing includes it.
3. Patches the CMake files: no OCCT/OpenCV/Assimp/Freetype, stub sources from
   `overrides/`, the `bambu-studio` target gets the generated GUI pieces.
4. A few small source patches for Emscripten (listed below).
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from cxx_items import split  # noqa: E402

BS = Path(sys.argv[1]).resolve()
GUI_SRC = BS / "src" / "_slic3r_gui" / "GUI"
GEN = BS / "wasm-gen"


def log(msg: str) -> None:
    print(f"[prepare] {msg}")


def patch(rel: str, pairs: list[tuple[str, str]], regex: bool = False, done: str | None = None) -> None:
    """Apply (old, new) replacements once. A pair counts as applied when `new` (or, for
    regex patches, the `done` marker) is already in the file; otherwise `old` must exist."""
    p = BS / rel
    text = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if regex:
            if done and done in text:
                continue
            if not re.search(old, text, flags=re.M):
                raise SystemExit(f"patch {rel}: pattern not found: {old[:80]!r}")
            text = re.sub(old, new, text, count=1, flags=re.M)
        else:
            if new and new in text:
                continue
            if old not in text:
                if new == "":
                    continue
                raise SystemExit(f"patch {rel}: text not found: {old[:80]!r}")
            text = text.replace(old, new, 1)
    if text.encode("utf-8") != p.read_bytes():
        p.write_text(text, encoding="utf-8", newline="\n")
        log(f"patched {rel}")


# ---------------------------------------------------------------------------
# 1. GUI pieces the CLI needs

# Drawing code: stubbed. Everything else in PartPlate.cpp is compiled unchanged; its
# GUI calls sit behind `if (m_plater)` (null in the CLI) or on paths the desktop CLI
# never takes, and the placeholder wxGetApp() aborts loudly if one is ever reached.
DRAWING = re.compile(
    r"glsafe|\bgl[A-Z]\w*\(|GLShader|GLModel|GLTexture|ImGui|imgui|m_bed3d|Bed3D|\bCamera\b|"
    r"wx(?:DC|MemoryDC|GCDC|GraphicsContext|Bitmap|Image|Font|Coord|Colour|Brush|Pen)\b|"
    r"get_view3D_canvas3D|\bTexturePart\b|\.render\(|\bGLVolume\b"
)

# Functions that touch drawing state only behind `if (m_plater)`; compiled unchanged.
KEEP_AS_IS = {
    "PartPlate::PartPlate", "PartPlate::~PartPlate", "PartPlate::init", "PartPlate::clear",
    "PartPlate::set_shape", "PartPlate::set_pos_and_size",
    "PartPlateList::PartPlateList", "PartPlateList::~PartPlateList", "PartPlateList::init",
    "PartPlateList::select_plate", "PartPlateList::set_shapes", "PartPlateList::reset_size",
    "PartPlateList::rebuild_plates_after_arrangement", "PartPlateList::load_from_3mf_structure",
    "PartPlateList::create_plate", "PartPlateList::delete_plate", "PartPlateList::clear",
    "PartPlateList::reset", "PartPlateList::reinit",
}


# Desktop theme colours (RenderColor / ImGui colours): no drawing here.
ALWAYS_STUB = {"PartPlate::update_render_colors", "PartPlate::load_render_colors",
               "PartPlate::calc_height_limit", "PartPlate::get_right_icon_offset_bed",
               # desktop-only pre-slice checks (translated messages, printer database);
               # the CLI does its own checks and only uses check_tpu_printable_status
               "PartPlate::check_filament_printable", "PartPlate::check_mixture_filament_compatible",
               "PartPlate::check_compatible_of_nozzle_and_filament",
               "PartPlate::check_flow_compatible_of_nozzle_and_filament",
               "PartPlate::check_tpu_nozzle_has_multiple_filaments",
               "PartPlate::check_high_temp_need_wrapping_detection",
               # 3D view state / background slicing of the desktop app
               "PartPlate::get_heat_soak_level", "PartPlate::update_slice_context",
               "PartPlateList::select_plate_view"}
# ... and every function whose name starts with "render" or mentions Helio (cloud service).
RENDER_NAME = re.compile(r"(^|::)render\w*$|helio", re.I)


def stub_body(header: str, name: str) -> str:
    short = name.split("::")[-1]
    owner = name.split("::")[-2] if "::" in name else ""
    if short == owner or short.startswith("~"):
        return "{}"
    pre = header.split("(")[0]
    rtype = pre[: pre.rfind(name.split("::")[0])].strip() if "::" in name else pre[: pre.rfind(short)].strip()
    rtype = re.sub(r"^(static|inline|virtual|constexpr|explicit)\s+", "", rtype).strip()
    if rtype in ("void", ""):
        return "{}"
    if rtype.endswith("&"):
        base = rtype[:-1].strip()
        return "{ static std::remove_cv_t<std::remove_reference_t<" + base + "&>> d{}; return d; }"
    return "{ return {}; }"


def stub_gui_functions(src: str, keep: set[str], file_name: str) -> tuple[str, list[str]]:
    out, stubbed = [], []
    for it in split(src):
        if it.kind == "func" and it.name not in keep and (DRAWING.search(it.text) or it.name in ALWAYS_STUB or RENDER_NAME.search(it.name)):
            # header = everything before the body's opening brace (initialiser lists stay)
            head, _sep, _body = it.text.partition("{")
            if re.search(r"\)\s*:\s*\w", head):          # constructor with init list
                head = re.split(r"\)\s*:\s*\w", head)[0] + ")"
            out.append(head.rstrip() + "\n" + stub_body(head, it.name) + "\n")
            stubbed.append(it.name)
        else:
            out.append(it.text)
    log(f"{file_name}: {len(stubbed)} drawing functions stubbed")
    return "".join(out), stubbed


def extract_functions(src: str, names: set[str]) -> str:
    return "\n".join(it.text.strip() + "\n" for it in split(src) if it.kind == "func" and it.name in names)


def put(path: Path, data: str | bytes) -> None:
    """Write only when the content changed, so a rerun does not trigger a full rebuild."""
    raw = data.encode("utf-8") if isinstance(data, str) else data
    if path.exists() and path.read_bytes() == raw:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def gen_gui() -> None:
    gui = BS / "src" / "slic3r" / "GUI"
    if gui.exists():
        (BS / "src" / "slic3r").rename(BS / "src" / "_slic3r_gui")
        log("moved src/slic3r to src/_slic3r_gui (not compiled)")
    out = GEN / "slic3r" / "GUI"
    # placeholder headers
    for f in (ROOT / "shim").rglob("*"):
        if f.is_file():
            put(GEN / f.relative_to(ROOT / "shim"), f.read_bytes())

    # PartPlate: header unchanged, source with drawing functions stubbed
    put(out / "PartPlate.hpp", (GUI_SRC / "PartPlate.hpp").read_bytes())
    src = (GUI_SRC / "PartPlate.cpp").read_text(encoding="utf-8")
    src, stubbed = stub_gui_functions(src, KEEP_AS_IS, "PartPlate.cpp")
    src = re.sub(r'#include <imgui/imgui_internal.h>\n', "", src)
    src = re.sub(r'#include <wx/dcgraph.h>\n', "", src)
    put(out / "PartPlate.cpp", src)
    put(GEN / "stubbed-functions.txt", "\n".join(stubbed) + "\n")

    # Wipe tower placement: plain logic, compiled as is
    for f in ("WipeTowerPlacement.hpp", "WipeTowerPlacement.cpp"):
        put(out / f, (GUI_SRC / f).read_bytes())

    # Colour maths used by the CLI's colour matching (plain code)
    utils_out = GEN / "slic3r" / "Utils"
    # (BBLUtil.hpp: libslic3r's LogSink includes it; its .cpp needs OpenSSL, not built)
    for f in ("ColorSpaceConvert.hpp", "BBLUtil.hpp"):
        put(utils_out / f, (GUI_SRC.parent / "Utils" / f).read_bytes())
    # ColorSpaceConvert.cpp without its two wxColour helpers
    csc = (GUI_SRC.parent / "Utils" / "ColorSpaceConvert.cpp").read_text(encoding="utf-8")
    csc = "".join(it.text for it in split(csc) if not (it.kind == "func" and "wxColour" in it.text))
    csc = re.sub(r"#include <wx/[^>]+>\n", "", csc)
    put(utils_out / "ColorSpaceConvert.cpp", csc)

    # Small pieces of other GUI files
    def one(src_text: str, name: str, must_contain: str) -> str:
        hits = [it.text.strip() for it in split(src_text)
                if it.kind == "func" and it.name == name and must_contain in it.text]
        if len(hits) != 1:
            raise SystemExit(f"{name} ({must_contain}): found {len(hits)} definitions")
        return hits[0]

    gc = (GUI_SRC / "GuiColor.cpp").read_text(encoding="utf-8")
    bc = (GUI_SRC / "BitmapCache.cpp").read_text(encoding="utf-8")
    pl = (GUI_SRC / "Plater.cpp").read_text(encoding="utf-8")
    gu = (GUI_SRC / "GUI_Utils.hpp").read_text(encoding="utf-8")
    extra = [
        "// Generated by tools/prepare.py from Bambu Studio's GUI_Utils.hpp, BitmapCache.cpp,",
        "// Plater.cpp and GuiColor.cpp: the few non-drawing functions the CLI needs.",
        '#include "BitmapCache.hpp"',
        '#include "Plater.hpp"',
        '#include "GuiColor.hpp"',
        "#include <array>",
        "#include <cmath>",
        "#include <cstring>",
        '#include "libslic3r/PrintConfig.hpp"',
        "#include <boost/algorithm/string.hpp>",
        "#include <boost/log/trivial.hpp>",
        "#include <boost/format.hpp>",
        "namespace Slic3r { namespace GUI {",
        one(gu, "hex_digit_to_int", "hex_digit_to_int"),
        extract_functions(bc, {"BitmapCache::parse_color", "BitmapCache::parse_color4"}),
        extract_functions(pl, {"get_min_flush_volumes"}),
        one(pl, "Plater::has_illegal_filename_characters", "const std::string& name"),
        one(gc, "calc_color_distance", "RGBA c1"),
        "}} // namespace Slic3r::GUI",
    ]
    put(out / "GuiExtract.cpp", "\n".join(extra))
    log("generated wasm-gen/slic3r/GUI")


# ---------------------------------------------------------------------------
# 2. CMake

def patch_cmake() -> None:
    # Root: GUI pieces + our includes before Bambu's src, no X11/DBus.
    patch("CMakeLists.txt", [
        ("include_directories(${LIBDIR})",
         "include_directories(BEFORE ${CMAKE_CURRENT_SOURCE_DIR}/wasm-gen ${CMAKE_CURRENT_SOURCE_DIR}/wasm-gen/slic3r/GUI)\n"
         "include_directories(${LIBDIR})"),
    ])

    # src: the CLI target gets the GUI pieces; no pango/X libs; Emscripten link options.
    patch("src/CMakeLists.txt", [
        # no resources symlink next to the web engine
        ('    add_custom_command(TARGET BambuStudio POST_BUILD\n        COMMAND ln -sfn "${SLIC3R_RESOURCES_DIR}" "${BIN_RESOURCES_DIR}"\n'
         '        COMMENT "Symlinking the resources directory into the build tree"\n        VERBATIM)',
         '    if (NOT EMSCRIPTEN)\n    add_custom_command(TARGET BambuStudio POST_BUILD\n        COMMAND ln -sfn "${SLIC3R_RESOURCES_DIR}" "${BIN_RESOURCES_DIR}"\n'
         '        COMMENT "Symlinking the resources directory into the build tree"\n        VERBATIM)\n    endif ()'),
        # no ffmpeg/.so copying for the web build
        ("    if (NOT APPLE AND NOT FLATPAK)\n        set(output_sos_Release \"\")",
         "    if (NOT APPLE AND NOT FLATPAK AND NOT EMSCRIPTEN)\n        set(output_sos_Release \"\")"),
        ("target_link_libraries(BambuStudio ${CMAKE_DL_LIBS} -lstdc++ Threads::Threads pangoft2-1.0)",
         "if (EMSCRIPTEN)\n"
         "    include(${BAMBU_WASM_DIR}/cmake/engine.cmake)\n"
         "else ()\n"
         "    target_link_libraries(BambuStudio ${CMAKE_DL_LIBS} -lstdc++ Threads::Threads pangoft2-1.0)\n"
         "endif ()"),
    ])

    # libslic3r: no OCCT / OpenCV / Assimp / Freetype. The modules that need them are
    # left out; overrides/libslic3r has OCCT/OpenCV-free versions of the two headers
    # other code includes, and wasm_stubs.cpp the functions the linker still asks for.
    left_out = [
        "Format/STEP.cpp", "Format/svg.cpp", "Format/AssimpImport.cpp", "Shape/TextShape.cpp",
        "SLA/Hollowing.cpp", "TexturePainting.cpp", "TextureToColor/TextureToColor.cpp",
        "TextureToColor/ColorUtils.cpp", "ObjColorUtils.cpp",
        "LogSink.cpp",   # encrypted log files + key download (OpenSSL, HTTP)
    ]
    lib = BS / "src" / "libslic3r"
    for hdr in (ROOT / "overrides" / "libslic3r").rglob("*.hpp"):
        put(lib / hdr.relative_to(ROOT / "overrides" / "libslic3r"), hdr.read_bytes())
    cm = (lib / "CMakeLists.txt").read_text(encoding="utf-8")
    for rel in left_out:
        cm, n = re.subn(r"(?m)^\s*" + re.escape(rel) + r"\s*\n", "", cm, count=1)
        if n != 1 and "wasm_stubs.cpp" not in cm:
            raise SystemExit(f"libslic3r CMakeLists: source {rel} not found")
    if "wasm_stubs.cpp" not in cm:
        cm += ("\n# WebAssembly build: stand-ins for the modules left out above.\n"
               "target_sources(libslic3r PRIVATE ${BAMBU_WASM_DIR}/overrides/libslic3r/wasm_stubs.cpp)\n")
    put(lib / "CMakeLists.txt", cm)
    log(f"left {len(left_out)} libslic3r modules out")
    patch("src/libslic3r/CMakeLists.txt", [
        # reproducible engine: no wall-clock build time in libslic3r_version.h
        ("string(TIMESTAMP COMPILE_TIME %Y%m%d-%H%M%S)",
         "if (EMSCRIPTEN)\n    set(COMPILE_TIME \"web\")\nelse ()\n    string(TIMESTAMP COMPILE_TIME %Y%m%d-%H%M%S)\nendif ()"),
        ("find_package(OpenCASCADE REQUIRED)", "if (NOT EMSCRIPTEN)\nfind_package(OpenCASCADE REQUIRED)\nendif ()"),
        ("set(OCCT_LIBS\n", "set(OCCT_LIBS_UNUSED\n"),
        ("if(NOT WIN32)\n    find_package(Freetype REQUIRED)", "if(NOT WIN32 AND NOT EMSCRIPTEN)\n    find_package(Freetype REQUIRED)"),
    ])


# ---------------------------------------------------------------------------
# 3. Small source patches for Emscripten

def patch_sources() -> None:
    patch("src/libslic3r/Platform.cpp", [
        (r'(\n\s*static_assert\s*\(\s*false\s*,\s*"Unknown platform detected"\s*\);)',
         r'\n#ifndef __EMSCRIPTEN__\1\n#endif'),
    ], regex=True, done="#ifndef __EMSCRIPTEN__")
    # The engine runs in a virtual file system: the "binary" lives in /bambu/bin, so
    # the CLI finds its printer profiles in /bambu/resources (written by the host page).
    patch("src/BambuStudio.cpp", [
        ("        install_path = boost::filesystem::canonical(boost::dll::program_location()).parent_path();",
         "#ifdef __EMSCRIPTEN__\n"
         "        install_path = boost::filesystem::path(\"/bambu/bin\");\n"
         "#else\n"
         "        install_path = boost::filesystem::canonical(boost::dll::program_location()).parent_path();\n"
         "#endif"),
    ])


def main() -> int:
    if not (BS / "src" / "BambuStudio.cpp").exists():
        raise SystemExit(f"not a Bambu Studio checkout: {BS}")
    gen_gui()
    patch_cmake()
    patch_sources()
    log("done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

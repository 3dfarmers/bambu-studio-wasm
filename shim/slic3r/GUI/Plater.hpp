#pragma once
// Placeholder for the desktop Plater (null in the CLI). Only get_min_flush_volumes()
// is real; tools/prepare.py extracts it from Bambu's Plater.cpp.
//
// Bambu's CLI reaches several libslic3r headers through the real GUI headers; they
// are included here so BambuStudio.cpp compiles unchanged.
#include <string>
#include <vector>
#include "libslic3r/PrintConfig.hpp"
#include "libslic3r/PresetBundle.hpp"
#include "libslic3r/BuildVolume.hpp"
#include "libslic3r/Point.hpp"
#include "I18N.hpp"
#include "Widgets/Label.hpp"
#include <wx/stdpaths.h>

// The desktop build gets an unqualified `string` from its GUI headers.
using std::string;

namespace Slic3r { namespace GUI {
class GLCanvas3D;
class Plater {
public:
    template<class... A> void mark_plate_toolbar_image_dirty(A&&...) {}
    template<class... A> void take_snapshot(A&&...) {}
    template<class... A> void set_bed_position(A&&...) {}
    template<class... A> void on_plate_layout_changed(A&&...) {}
    template<class... A> void update(A&&...) {}
    template<class... A> void set_global_filament_map(A&&...) {}
    std::vector<int> get_global_filament_map() const { return {}; }
    bool is_gcode_3mf() const { return false; }
    bool only_gcode_mode() const { return false; }
    const VendorProfile::PrinterModel* get_curr_printer_model() const { return nullptr; }
    template<class... A> void reset_gcode_toolpaths(A&&...) {}
    bool is_preview_shown() const { return false; }
    const GLCanvas3D* get_view3D_canvas3D() const { return nullptr; }
    template<class... A> static void show_illegal_characters_warning(A&&...) {}
    static bool has_illegal_filename_characters(const std::string& name);   // real, from Plater.cpp
};
std::vector<int> get_min_flush_volumes(const DynamicPrintConfig &full_config, size_t nozzle_id);
}}

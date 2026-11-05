#pragma once
// Placeholder for the desktop application object. Only names used by Bambu's plate
// code; wxGetApp() returns an empty app (see GuiAppStub.cpp).
#include <string>
#include <vector>
#include <wx/string.h>
#include "libslic3r/PresetBundle.hpp"
#include "libslic3r/AppConfig.hpp"
#include "I18N.hpp"
#include "Plater.hpp"
#include "format.hpp"

#define wxID_YES 5103
#define wxID_NO 5104

#include <boost/nowide/fstream.hpp>

namespace Slic3r { namespace GUI {
class PartPlate;
struct ObjectDataViewModel { template<class... A> void SetCurSelectedPlateFullName(A&&...) {} };
class ObjectList {
public:
    template<class... A> void reload_all_plates(A&&...) {}
    template<class... A> void on_plate_added(A&&...) {}
    template<class... A> void on_plate_deleted(A&&...) {}
    template<class... A> void update_info_items(A&&...) {}
    template<class... A> void update_plate_values_for_items(A&&...) {}
    template<class... A> ObjectDataViewModel* GetModel(A&&...) { return nullptr; }
};
class TabPrintPlate {
public:
    template<class... A> int show_spiral_mode_settings_dialog(A&&...) { return wxID_NO; }
};
class GUI_App {
public:
    PresetBundle* preset_bundle{nullptr};
    AppConfig*    app_config{nullptr};
    void*         plate_tab{nullptr};
    Plater*       plater() { return nullptr; }
    ObjectList*   obj_list() { return nullptr; }
    bool          dark_mode() const { return false; }
    int           filaments_cnt() const { return 0; }
    PrintSequence global_print_sequence() const { return PrintSequence::ByLayer; }
    std::string   current_language_code_safe() const { return "en"; }
};
GUI_App& wxGetApp();
}}

#pragma once
// Placeholder: the desktop GUI's 3D scene. Only names used by the CLI and plate code.
#include <array>
#include <memory>
#include <string>
#include <vector>
#include <wx/string.h>
#include "libslic3r/Point.hpp"
#include "libslic3r/BoundingBox.hpp"
#include "libslic3r/Model.hpp"
#include "GLModel.hpp"
namespace Slic3r {
namespace UndoRedo { class StackImpl; }
class GLVolume {
public:
    bool printable{true};
    bool is_modifier{false};
    bool is_wipe_tower{false};
    template<class... A> void set_render_color(A&&...) {}
    template<class... A> void set_color(A&&...) {}
    BoundingBoxf3 transformed_bounding_box() const { return {}; }
    BoundingBoxf3 transformed_convex_hull_bounding_box() const { return {}; }
};
class GLVolumeCollection {
public:
    std::vector<GLVolume*> volumes;
    ~GLVolumeCollection() { for (auto* v : volumes) delete v; }
    int load_object_volume(const ModelObject*, int, int, int, const std::string&, bool = false, bool = false, bool = false, bool = false)
    { volumes.push_back(new GLVolume()); return int(volumes.size()) - 1; }
    void clear() { for (auto* v : volumes) delete v; volumes.clear(); }
};
}

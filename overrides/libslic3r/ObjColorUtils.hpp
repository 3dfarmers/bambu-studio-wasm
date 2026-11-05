#pragma once
// WebAssembly build: Bambu Studio's ObjColorUtils.hpp without OpenCV. Colour
// clustering for OBJ/3MF colour import is not part of this build.
#include <map>
#include <string>
#include <unordered_map>
#include <vector>
#include "libslic3r/Color.hpp"

namespace Slic3r {
class Model;
struct TriangleColor;
struct VolumeColorInfo;
struct TexturedMesh;
}

bool obj_color_deal_algo(std::vector<Slic3r::RGBA> &input_colors,
                         std::vector<Slic3r::RGBA> &cluster_colors_from_algo,
                         std::vector<int> &         cluster_labels_from_algo,
                         char &                     cluster_number,
                         int                        max_cluster);

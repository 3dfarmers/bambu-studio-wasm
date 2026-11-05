#pragma once
// WebAssembly build: Bambu Studio's GuiColor.hpp without wxColour.
#include "libslic3r/Color.hpp"
#include "slic3r/Utils/ColorSpaceConvert.hpp"

struct ColorDistValue
{
    int   id;
    float distance;
};

namespace Slic3r { namespace GUI {
float calc_color_distance(RGBA c1, RGBA c2);
}}

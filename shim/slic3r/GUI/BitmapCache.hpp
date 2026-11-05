#pragma once
#include <string>
namespace Slic3r { namespace GUI {
class BitmapCache {
public:
    static bool parse_color(const std::string& scolor, unsigned char* rgb_out);
    static bool parse_color4(const std::string& scolor, unsigned char* rgba_out);
};
}}

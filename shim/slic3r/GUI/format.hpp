#pragma once
// Bambu's GUI format helpers, on top of libslic3r's Slic3r::format().
#include <string>
#include "libslic3r/format.hpp"
#include "I18N.hpp"
namespace Slic3r { namespace GUI {
template<typename... TArgs>
inline std::string format(const char* fmt, TArgs&&... args) { return Slic3r::format(fmt, std::forward<TArgs>(args)...); }
template<typename... TArgs>
inline std::string format(const std::string& fmt, TArgs&&... args) { return Slic3r::format(fmt, std::forward<TArgs>(args)...); }
template<typename... TArgs>
inline wxString format_wxstr(const std::string& fmt, TArgs&&... args) { return wxString(Slic3r::format(fmt, std::forward<TArgs>(args)...)); }
}}

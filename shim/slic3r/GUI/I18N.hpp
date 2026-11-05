#pragma once
// Placeholder: no translations in the WebAssembly slicer.
#include <wx/string.h>
#ifndef _L
#define _L(s) wxString(s)
#endif
#ifndef _u8L
#define _u8L(s) std::string(s)
#endif
#ifndef L
#define L(s) s
#endif

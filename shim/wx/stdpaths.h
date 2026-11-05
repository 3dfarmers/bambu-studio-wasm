#pragma once
// Placeholder: the CLI asks wx for the temp folder; in the engine it is /tmp.
#include <wx/string.h>
class wxFileName {
public:
    static wxString GetTempDir() { return wxString("/tmp"); }
};

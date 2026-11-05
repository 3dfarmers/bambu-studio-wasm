#pragma once
// Placeholder wxString: a std::string with the few wx methods the CLI uses.
#include <string>
#include <vector>
class wxString : public std::string {
public:
    using std::string::string;
    wxString() = default;
    wxString(const std::string& s) : std::string(s) {}
    std::string ToStdString() const { return *this; }
    std::string ToUTF8() const { return *this; }
    std::string utf8_str() const { return *this; }
    std::string utf8_string() const { return *this; }
    static wxString FromUTF8(const std::string& s) { return wxString(s); }
    template<class... A> static wxString Format(const char* f, A&&...) { return wxString(f); }
    bool IsEmpty() const { return empty(); }
};
// The desktop build gets unqualified `string` / `vector` from its GUI headers.
using std::string;
using std::vector;
using std::insert_iterator;

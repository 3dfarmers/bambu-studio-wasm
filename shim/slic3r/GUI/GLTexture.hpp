#pragma once
// Placeholder: textures are only drawn by the desktop GUI.
#include <string>
#include <vector>
#include <GL/glew.h>
#include <wx/string.h>
namespace Slic3r { namespace GUI {
class GLTexture {
public:
    struct UV { float u{0}, v{0}; };
    struct Quad_UVs { UV left_bottom, right_bottom, right_top, left_top; };
    static Quad_UVs FullTextureUVs;
    template<class... A> bool load_from_file(A&&...) { return false; }
    template<class... A> bool load_from_svg_file(A&&...) { return false; }
    template<class... A> bool generate_from_text_string(A&&...) { return false; }
    template<class... A> bool generate_from_text(A&&...) { return false; }
    void reset() {}
    unsigned int get_id() const { return 0; }
    int get_width() const { return 0; }
    int get_height() const { return 0; }
    int m_original_width{0};
    int m_original_height{0};
    template<class... A> static void render_texture(A&&...) {}
    template<class... A> static void render_sub_texture(A&&...) {}
};
}}

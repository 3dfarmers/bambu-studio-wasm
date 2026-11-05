// The placeholder application object. In Bambu's command-line slicer there is no
// app: plate code checks `&wxGetApp() && wxGetApp().plater()` or `if (m_plater)` and
// skips the desktop-only part. Here wxGetApp() returns an empty app whose plater(),
// obj_list() and preset_bundle are null, so those checks skip the same way.
#include "GUI_App.hpp"
#include "GLTexture.hpp"
namespace Slic3r { namespace GUI {
GUI_App& wxGetApp()
{
    static GUI_App app;
    return app;
}
GLTexture::Quad_UVs GLTexture::FullTextureUVs{};
}}

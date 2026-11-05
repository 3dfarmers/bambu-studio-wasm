#pragma once
// Placeholder: thumbnails are not rendered in the WebAssembly slicer.
#include <memory>
#include "OpenGLManager.hpp"
#include "Camera.hpp"
#include "3DScene.hpp"
#include "libslic3r/GCode/ThumbnailData.hpp"
namespace Slic3r { namespace GUI {
class GLCanvas3D {
public:
    template<class... A> static void render_thumbnail_framebuffer(A&&...) {}
    template<class... A> static void render_thumbnail_legacy(A&&...) {}
};
}}

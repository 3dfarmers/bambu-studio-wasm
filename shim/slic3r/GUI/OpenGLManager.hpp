#pragma once
// Placeholder: init_gl() fails, so the CLI writes files without rendered thumbnails.
#include <memory>
#include <string>
#include <GL/glew.h>
namespace Slic3r {
class GLShaderProgram {
public:
    template<class... A> void set_uniform(A&&...) {}
    void start_using() const {}
    void stop_using() const {}
};
namespace GUI {
class OpenGLManager {
public:
    enum class EFramebufferType : unsigned char { Unknown, Arb, Ext };
    void set_legacy_framebuffer_enabled(bool) {}
    bool init_gl(bool = false) { return false; }
    std::shared_ptr<GLShaderProgram> get_shader(const std::string&) { return nullptr; }
    template<class... A> void bind_shader(A&&...) {}
    void unbind_shader() {}
    void bind_vao() {}
    void unbind_vao() {}
    static bool are_framebuffers_supported() { return false; }
    static EFramebufferType get_framebuffers_type() { return EFramebufferType::Unknown; }
    static std::string framebuffer_type_to_string(EFramebufferType) { return "unknown"; }
};
}}

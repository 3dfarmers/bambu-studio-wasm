#pragma once
// Placeholder: models are only drawn by the desktop GUI.
#include <array>
#include <vector>
#include <string>
#include "libslic3r/Point.hpp"
#include "libslic3r/Polygon.hpp"
#include "libslic3r/ExPolygon.hpp"
#include "libslic3r/TriangleMesh.hpp"
namespace Slic3r { namespace GUI {
class GLModel {
public:
    struct Geometry {
        enum class EPrimitiveType : unsigned char { Points, Triangles, TriangleStrip, TriangleFan, Lines, LineStrip, LineLoop };
        enum class EVertexLayout : unsigned char { P2, P2T2, P3, P3T2, P3N3, P3N3T2 };
        enum class EIndexType : unsigned char { UINT, USHORT, UBYTE };
        struct Format { EPrimitiveType type{EPrimitiveType::Triangles}; EVertexLayout vertex_layout{EVertexLayout::P3N3}; };
        Format format;
        std::vector<float> vertices;
        std::vector<unsigned int> indices;
        template<class... A> void add_vertex(A&&...) {}
        template<class... A> void add_triangle(A&&...) {}
        template<class... A> void add_line(A&&...) {}
        template<class... A> void reserve_vertices(A&&...) {}
        template<class... A> void reserve_indices(A&&...) {}
        size_t vertices_count() const { return 0; }
        size_t indices_count() const { return 0; }
    };
    template<class... A> void init_from(A&&...) {}
    template<class... A> bool init_model_from_poly(A&&...) { return false; }
    template<class... A> bool init_model_from_lines(A&&...) { return false; }
    template<class... A> void render_geometry(A&&...) const {}
    template<class... A> void set_visible(A&&...) {}
    template<class... A> void set_color(A&&...) {}
    template<class... A> void render(A&&...) const {}
    void reset() {}
    bool is_initialized() const { return false; }
    bool is_empty() const { return true; }
};
}}

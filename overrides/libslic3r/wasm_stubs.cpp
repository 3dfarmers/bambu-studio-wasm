// Stand-ins for the Bambu Studio pieces this build leaves out (see tools/prepare.py).
// Each one reports "not available" the way the real function reports a failure.
// The list is exactly what the linker asks for; nothing on the slicing path is here.
#include <pthread.h>
#include <string>
#include <vector>
#include "libslic3r/LogSink.hpp"
#include "libslic3r/ObjColorUtils.hpp"
#include "libslic3r/TexturePainting.hpp"
#include "libslic3r/Format/AssimpImport.hpp"

// OBJ colour clustering (OpenCV): not available.
bool obj_color_deal_algo(std::vector<Slic3r::RGBA> &, std::vector<Slic3r::RGBA> &, std::vector<int> &, char &cluster_number, int)
{
    cluster_number = 0;
    return false;
}

namespace Slic3r {

// Encrypted log files (LogSink.cpp, OpenSSL + HTTP) are not built: logs go to the console.
bool LogSinkBackend::is_consuming_on_this_thread() { return false; }

// OBJ/glTF texture import (Assimp) is not built.
bool load_assimp_textured_model(const std::string &, TexturedMesh &, std::string *error_message)
{
    if (error_message)
        *error_message = "Textured OBJ/glTF import is not available in the web slicer.";
    return false;
}

} // namespace Slic3r

// Emscripten has no thread names; Bambu only uses them for debugging.
extern "C" int pthread_setname_np(pthread_t, const char *) { return 0; }

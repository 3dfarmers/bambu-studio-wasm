#ifndef slic3r_Format_STEP_hpp_
#define slic3r_Format_STEP_hpp_
// WebAssembly build: Bambu Studio's STEP.hpp without OpenCASCADE. STEP import is
// not part of this build; loading a .step file fails cleanly.
#include <atomic>
#include <functional>
#include <string>
#include <vector>
#include <boost/filesystem/path.hpp>
#include "libslic3r/Log.hpp"

namespace fs = boost::filesystem;

namespace Slic3r {
class Model;
class TriangleMesh;
class ModelObject;

const int LOAD_STEP_STAGE_READ_FILE          = 0;
const int LOAD_STEP_STAGE_GET_SOLID          = 1;
const int LOAD_STEP_STAGE_GET_MESH           = 2;
const int LOAD_STEP_STAGE_NUM                = 3;
const int LOAD_STEP_STAGE_UNIT_NUM           = 5;

typedef std::function<void(int load_stage, int current, int total, bool& cancel)> ImportStepProgressFn;
typedef std::function<void(bool isUtf8)> StepIsUtf8Fn;

struct StepImportTreeNode
{
    size_t              id{0};
    size_t              parent_id{0};
    std::vector<size_t> children;
    std::string         name;
    std::string         shape_type;
    std::string         object_name;
    std::string         object_key;
    int                 model_object_idx{-1};
    bool                is_reference{false};
    bool                has_shape{false};
    int                 component_count{0};
};

inline bool load_step(const char *, Model *, bool &, double = 0.003, double = 0.5, bool = false,
                      ImportStepProgressFn = nullptr, StepIsUtf8Fn = nullptr, long & = *(new long(-1)))
{ return false; }

class StepPreProcessor {
public:
    bool preprocess(const char *, std::string &) { return false; }
    static bool isUtf8File(const char *) { return true; }
    static bool isUtf8(const std::string) { return true; }
};

class Step
{
public:
    enum class Step_Status { LOAD_SUCCESS, LOAD_ERROR, CANCEL, MESH_SUCCESS, MESH_ERROR };
    Step(fs::path path, ImportStepProgressFn stepFn = nullptr, StepIsUtf8Fn isUtf8Fn = nullptr) : m_path(path.string()) {}
    Step(std::string path, ImportStepProgressFn stepFn = nullptr, StepIsUtf8Fn isUtf8Fn = nullptr) : m_path(path) {}
    Step_Status load() { return Step_Status::LOAD_ERROR; }
    void dump_structure_tree() const {}
    unsigned int get_triangle_num(double, double) { return 0; }
    unsigned int get_triangle_num_tbb(double, double) { return 0; }
    void clean_mesh_data() {}
    Step_Status mesh(Model *, bool &, bool, double = 0.003, double = 0.5) { return Step_Status::MESH_ERROR; }
    std::atomic<bool> m_stop_mesh{false};
    void update_process(int, int, int, bool &) {}
    const std::vector<std::string>& get_unclosed_shells() const { return m_unclosed_shells; }
private:
    std::string m_path;
    std::vector<std::string> m_unclosed_shells;
};
} // namespace Slic3r
#endif

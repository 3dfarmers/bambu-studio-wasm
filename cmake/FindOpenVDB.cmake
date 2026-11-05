# WebAssembly build: OpenVDB (SLA hollowing only) is not built. Report it as found so
# Bambu's top-level CMake does not stop, but create no target: libslic3r then leaves
# OpenVDBUtils out.
set(OpenVDB_FOUND TRUE)
set(OPENVDB_FOUND TRUE)

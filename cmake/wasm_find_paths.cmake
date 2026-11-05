# Loaded before Bambu Studio's top-level project() (CMAKE_PROJECT_INCLUDE_BEFORE).
# Emscripten's toolchain only searches its sysroot; our dependencies live in
# deps-install, so search both.
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)

# Emscripten threads come from the -pthread flag, not from a library.
if(NOT TARGET Threads::Threads)
    add_library(Threads::Threads INTERFACE IMPORTED GLOBAL)
    set_target_properties(Threads::Threads PROPERTIES INTERFACE_COMPILE_OPTIONS "-pthread")
endif()
set(Threads_FOUND TRUE)
set(CMAKE_THREAD_LIBS_INIT "")

add_compile_definitions(SLIC3R_WASM=1)

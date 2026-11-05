# WebAssembly build: Assimp (OBJ/glTF texture import) is not built; empty target.
if(NOT TARGET assimp::assimp)
  add_library(assimp::assimp INTERFACE IMPORTED GLOBAL)
endif()
set(assimp_FOUND TRUE)

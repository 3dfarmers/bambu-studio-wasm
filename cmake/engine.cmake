# Included from Bambu Studio's src/CMakeLists.txt (patched by tools/prepare.py) for
# the WebAssembly build of the `bambu-studio` command-line target.
set(_gen ${CMAKE_SOURCE_DIR}/wasm-gen)
target_sources(BambuStudio PRIVATE
    ${_gen}/slic3r/GUI/PartPlate.cpp
    ${_gen}/slic3r/GUI/WipeTowerPlacement.cpp
    ${_gen}/slic3r/GUI/GuiExtract.cpp
    ${_gen}/slic3r/GUI/GuiAppStub.cpp
    ${_gen}/slic3r/Utils/ColorSpaceConvert.cpp
)
set_target_properties(BambuStudio PROPERTIES OUTPUT_NAME "bambu-slicer" SUFFIX ".js")
target_link_options(BambuStudio PRIVATE
    -O3
    -fwasm-exceptions
    -sSUPPORT_LONGJMP=wasm
    -pthread
    -sPROXY_TO_PTHREAD=1
    -sPTHREAD_POOL_SIZE=navigator.hardwareConcurrency+2
    -sMALLOC=mimalloc
    -sALLOW_MEMORY_GROWTH=1
    -sINITIAL_MEMORY=268435456
    -sMAXIMUM_MEMORY=4294967296
    -sSTACK_SIZE=16777216
    -sMODULARIZE=1
    -sEXPORT_NAME=BambuSlicer
    -sINVOKE_RUN=0
    -sEXIT_RUNTIME=0
    -sENVIRONMENT=web,worker,node
    -sFORCE_FILESYSTEM=1
    "-sEXPORTED_RUNTIME_METHODS=['callMain','FS','HEAP8']"
)

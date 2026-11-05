Placeholder headers for the few Bambu Studio GUI types that the command-line
slicer and the plate code mention. tools/prepare.py copies them into the build's
`wasm-gen/` folder. They only have to compile: the CLI runs without a window
(no Plater, glfwInit() fails), so none of these placeholders do real work.

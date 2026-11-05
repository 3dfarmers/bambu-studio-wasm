#pragma once
// Placeholder GLFW: glfwInit() fails, so the CLI skips thumbnail rendering.
#include <GL/glew.h>
#define GLFW_TRUE 1
#define GLFW_FALSE 0
#define GLFW_CONTEXT_VERSION_MAJOR 0x00022002
#define GLFW_CONTEXT_VERSION_MINOR 0x00022003
#define GLFW_RED_BITS 0x00021001
#define GLFW_GREEN_BITS 0x00021002
#define GLFW_BLUE_BITS 0x00021003
#define GLFW_ALPHA_BITS 0x00021004
#define GLFW_VISIBLE 0x00020004
#define GLFW_OPENGL_PROFILE 0x00022008
#define GLFW_OPENGL_CORE_PROFILE 0x00032001
#define GLFW_OPENGL_COMPAT_PROFILE 0x00032002
#define GLFW_OPENGL_FORWARD_COMPAT 0x00022006
#define GLFW_CONTEXT_CREATION_API 0x0002200B
#define GLFW_OSMESA_CONTEXT_API 0x00036003
#define GLFW_EGL_CONTEXT_API 0x00036002
#define GLFW_NATIVE_CONTEXT_API 0x00036001
typedef struct GLFWwindow GLFWwindow;
typedef void (*GLFWerrorfun)(int, const char*);
inline void glfwGetVersion(int* a, int* b, int* c) { if (a) *a = 3; if (b) *b = 3; if (c) *c = 0; }
inline GLFWerrorfun glfwSetErrorCallback(GLFWerrorfun) { return nullptr; }
inline int glfwInit() { return GLFW_FALSE; }
inline int glfwGetError(const char** d) { if (d) *d = "no OpenGL in WebAssembly"; return 0x00010001; }
inline void glfwWindowHint(int, int) {}
inline GLFWwindow* glfwCreateWindow(int, int, const char*, void*, void*) { return nullptr; }
inline void glfwMakeContextCurrent(GLFWwindow*) {}
inline void glfwDestroyWindow(GLFWwindow*) {}
inline void glfwTerminate() {}

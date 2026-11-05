#pragma once
// Placeholder: no OpenGL in the WebAssembly slicer.
typedef unsigned int GLuint;
typedef int GLint;
typedef unsigned int GLenum;
typedef float GLfloat;
typedef unsigned char GLboolean;
typedef int GLsizei;
#define GL_TRUE 1
#define GL_FALSE 0
#define glsafe(cmd) do {} while (0)

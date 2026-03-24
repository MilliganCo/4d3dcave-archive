#version 330 core

layout(location = 0) in vec3 position;

uniform mat4 mvp;
uniform vec3 glow_pos;
uniform float glow_size;

out vec3 glow_color;

void main() {
    vec3 pos = glow_pos + position * glow_size;
    gl_Position = mvp * vec4(pos, 1.0);
    glow_color = vec3(1.0, 0.8, 0.3); // Желто-оранжевый цвет свечения
}


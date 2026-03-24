#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

uniform mat4 mvp;
uniform mat4 model;

out vec3 normal_ws;
out vec3 pos_ws;

void main() {
    vec4 pos = model * vec4(position, 1.0);
    pos_ws = pos.xyz;
    normal_ws = mat3(model) * normal;
    gl_Position = mvp * vec4(position, 1.0);
}


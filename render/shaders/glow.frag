#version 330 core

in vec3 glow_color;

uniform float intensity;

out vec4 frag_color;

void main() {
    frag_color = vec4(glow_color * intensity, 1.0);
}


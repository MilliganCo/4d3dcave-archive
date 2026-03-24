#version 330 core

in vec3 normal_ws;
in vec3 pos_ws;

uniform vec3 light_pos;
uniform vec3 light_dir;
uniform float light_angle;
uniform float light_range;
uniform vec3 light_color;
uniform float fog_distance;
uniform vec3 fog_color;

out vec4 frag_color;

void main() {
    // Ламбертово затенение
    vec3 n = normalize(normal_ws);
    vec3 to_light = normalize(light_pos - pos_ws);
    
    // Проверка угла конуса фонарика
    float angle = acos(dot(to_light, normalize(-light_dir)));
    if (angle > light_angle) {
        frag_color = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    // Расстояние до света
    float dist = length(light_pos - pos_ws);
    float attenuation = 1.0 / (1.0 + 0.1 * dist + 0.01 * dist * dist);
    attenuation *= smoothstep(light_range, 0.0, dist);
    
    // Диффузное освещение
    float ndotl = max(dot(n, to_light), 0.0);
    vec3 diffuse = light_color * ndotl * attenuation;
    
    // Трипланарное текстурирование (упрощенное - просто серый цвет)
    vec3 color = vec3(0.3, 0.3, 0.35) + diffuse * 0.5;
    
    // Туман
    float fog_factor = smoothstep(0.0, fog_distance, dist);
    color = mix(color, fog_color, fog_factor);
    
    frag_color = vec4(color, 1.0);
}


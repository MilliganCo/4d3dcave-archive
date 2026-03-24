import * as THREE from 'three';

export type ShadowQuality = 'low' | 'med' | 'high';

const SHADOW_MAP_SIZES: Record<ShadowQuality, number> = {
    low: 1024,
    med: 2048,
    high: 4096
};

/** Настройка системы теней. */
export function enableShadows(
    renderer: THREE.WebGLRenderer,
    quality: ShadowQuality = 'med'
): void {
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.shadowMap.autoUpdate = true;
}

/** Создание SpotLight с настройками теней. */
export function setupSpotLight(
    color: number = 0xffffff,
    intensity: number = 3.0,
    distance: number = 80,
    angle: number = 0.9,
    penumbra: number = 0.35,
    decay: number = 2,
    quality: ShadowQuality = 'med'
): THREE.SpotLight {
    const light = new THREE.SpotLight(
        color,
        intensity,
        distance,
        angle,
        penumbra,
        decay
    );
    
    light.castShadow = true;
    const mapSize = SHADOW_MAP_SIZES[quality];
    light.shadow.mapSize.width = mapSize;
    light.shadow.mapSize.height = mapSize;
    light.shadow.bias = -0.0002;
    light.shadow.normalBias = 0.5;
    light.shadow.camera.near = 0.5;
    light.shadow.camera.far = 80;
    
    return light;
}


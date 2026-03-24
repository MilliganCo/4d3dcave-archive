import * as THREE from 'three';

/** Постобработка (опционально FXAA). */
export class PostProcessor {
    private composer?: any; // THREE.EffectComposer (если используется)
    
    constructor() {
        // В MVP постобработка не обязательна
        // Можно добавить FXAA через THREE.EffectComposer если нужно
    }
    
    render(renderer: THREE.WebGLRenderer, scene: THREE.Scene, camera: THREE.Camera): void {
        // Прямой рендер без постобработки в MVP
        renderer.render(scene, camera);
    }
}


import * as THREE from 'three';
import { LightCurve } from '../core/curve';
import { HiddenCaster } from '../core/hit';
import { ObjectPlacer, PlacementConfig } from '../core/placement';
import { setupSpotLight, ShadowQuality } from '../render/shadows';

export interface WorldConfig {
    sceneSize: number;
    difficulty: 'easy' | 'normal' | 'hard';
    shadowQuality: ShadowQuality;
    lightSpeed: number;
    lightPauseDuration: number;
    lightCooldown: number;
    hitMaxDist: number;
    hitTolerance: number;
}

const DIFFICULTY_TARGETS = {
    easy: 7,
    normal: 10,
    hard: 13
};

/** Мир игры. */
export class World {
    scene: THREE.Scene;
    receivers: THREE.Object3D[] = [];
    casters: HiddenCaster[] = [];
    lightRig: THREE.Object3D;
    light: THREE.SpotLight;
    lightCurve: LightCurve;
    private config: WorldConfig;
    
    constructor(config: WorldConfig) {
        this.config = config;
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0d0f13);
        
        // Настройка света
        this.setupLight();
        
        // Построение сцены и размещение объектов будет выполнено отдельно
    }
    
    private setupLight(): void {
        // Создаем SpotLight
        this.light = setupSpotLight(
            0xffffff,
            3.0,
            80,
            0.9,
            0.35,
            2,
            this.config.shadowQuality
        );
        
        // Rig для движения света
        this.lightRig = new THREE.Object3D();
        this.lightRig.add(this.light);
        this.lightRig.add(this.light.target);
        this.scene.add(this.lightRig);
        
        // Создаем траекторию света
        const points = this.generateLightPath();
        this.lightCurve = new LightCurve(points, this.config.lightSpeed);
        
        // Добавляем слабое окружающее освещение для видимости сцены
        const ambientLight = new THREE.AmbientLight(0x404040, 0.2);
        this.scene.add(ambientLight);
    }
    
    private generateLightPath(): THREE.Vector3[] {
        const half = this.config.sceneSize / 2;
        const height = 8;
        
        // Контрольные точки для траектории света
        return [
            new THREE.Vector3(-half * 0.7, height, -half * 0.7),
            new THREE.Vector3(half * 0.3, height, -half * 0.8),
            new THREE.Vector3(half * 0.8, height, -half * 0.2),
            new THREE.Vector3(half * 0.6, height, half * 0.6),
            new THREE.Vector3(-half * 0.2, height, half * 0.8),
            new THREE.Vector3(-half * 0.8, height, half * 0.3),
            new THREE.Vector3(-half * 0.9, height, -half * 0.4),
        ];
    }
    
    /** Обновление мира. */
    update(dt: number): void {
        // Обновление движения света
        this.lightCurve.update(dt);
        const pos = this.lightCurve.getPosition();
        const tangent = this.lightCurve.getTangent();
        
        this.lightRig.position.copy(pos);
        
        // Направляем свет вдоль траектории
        const targetPos = pos.clone().add(tangent.clone().multiplyScalar(10));
        this.light.target.position.copy(targetPos);
    }
    
    /** Остановить свет. */
    pauseLight(duration: number): void {
        this.lightCurve.pause(duration);
    }
    
    /** Проверка, остановлен ли свет. */
    isLightPaused(): boolean {
        return this.lightCurve.isPaused();
    }
    
    /** Сброс мира. */
    reset(): void {
        this.lightCurve.reset();
        this.casters.forEach(c => c.found = false);
    }
}


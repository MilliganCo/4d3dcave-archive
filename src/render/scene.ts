import * as THREE from 'three';
import { ObjectPlacer, PlacementConfig } from '../core/placement';

/** Построение сцены с приёмниками теней. */
export class SceneBuilder {
    private scene: THREE.Scene;
    private receivers: THREE.Object3D[] = [];
    
    constructor(scene: THREE.Scene) {
        this.scene = scene;
    }
    
    /** Построить сцену с приёмниками теней. */
    buildReceivers(sceneSize: number): THREE.Object3D[] {
        this.receivers = [];
        
        // Пол
        const floor = this.createFloor(sceneSize);
        this.scene.add(floor);
        this.receivers.push(floor);
        
        // Стены
        const walls = this.createWalls(sceneSize);
        walls.forEach(wall => {
            this.scene.add(wall);
            this.receivers.push(wall);
        });
        
        // Арки и мосты
        const arches = this.createArches(sceneSize);
        arches.forEach(arch => {
            this.scene.add(arch);
            this.receivers.push(arch);
        });
        
        return this.receivers;
    }
    
    private createFloor(size: number): THREE.Mesh {
        const geometry = new THREE.PlaneGeometry(size, size);
        geometry.rotateX(-Math.PI / 2);
        
        // ShadowMaterial для теней
        const shadowMat = new THREE.ShadowMaterial({ opacity: 0.72 });
        shadowMat.depthWrite = true;
        
        // Дополнительный материал для фактуры (опционально)
        const baseMat = new THREE.MeshLambertMaterial({
            color: 0x2a2a2a,
            transparent: true,
            opacity: 0.2
        });
        
        const floor = new THREE.Mesh(geometry, shadowMat);
        floor.position.y = 0;
        floor.receiveShadow = true;
        
        return floor;
    }
    
    private createWalls(size: number): THREE.Mesh[] {
        const walls: THREE.Mesh[] = [];
        const half = size / 2;
        const wallHeight = 8;
        const wallThickness = 0.5;
        
        // Стены по периметру и внутри
        const wallConfigs = [
            // Внешние стены
            { pos: [half, wallHeight / 2, 0], size: [wallThickness, wallHeight, size] },
            { pos: [-half, wallHeight / 2, 0], size: [wallThickness, wallHeight, size] },
            { pos: [0, wallHeight / 2, half], size: [size, wallHeight, wallThickness] },
            { pos: [0, wallHeight / 2, -half], size: [size, wallHeight, wallThickness] },
            // Внутренние стены
            { pos: [half * 0.3, wallHeight / 2, half * 0.4], size: [wallThickness, wallHeight * 0.8, size * 0.3] },
            { pos: [-half * 0.3, wallHeight / 2, -half * 0.4], size: [wallThickness, wallHeight * 0.9, size * 0.35] },
            { pos: [half * 0.5, wallHeight / 2, -half * 0.2], size: [size * 0.25, wallHeight * 0.7, wallThickness] },
            { pos: [-half * 0.5, wallHeight / 2, half * 0.2], size: [size * 0.3, wallHeight * 0.85, wallThickness] },
        ];
        
        for (const config of wallConfigs) {
            const geometry = new THREE.BoxGeometry(...config.size);
            const material = new THREE.ShadowMaterial({ opacity: 0.7 });
            material.depthWrite = true;
            
            const wall = new THREE.Mesh(geometry, material);
            wall.position.set(...config.pos);
            wall.receiveShadow = true;
            walls.push(wall);
        }
        
        return walls;
    }
    
    private createArches(size: number): THREE.Mesh[] {
        const arches: THREE.Mesh[] = [];
        const half = size / 2;
        
        // Несколько арок/мостов
        const archConfigs = [
            { pos: [half * 0.2, 5, half * 0.3], size: [size * 0.15, 1, size * 0.2] },
            { pos: [-half * 0.2, 6, -half * 0.3], size: [size * 0.2, 1.2, size * 0.15] },
        ];
        
        for (const config of archConfigs) {
            const geometry = new THREE.BoxGeometry(...config.size);
            const material = new THREE.ShadowMaterial({ opacity: 0.65 });
            material.depthWrite = true;
            
            const arch = new THREE.Mesh(geometry, material);
            arch.position.set(...config.pos);
            arch.receiveShadow = true;
            arches.push(arch);
        }
        
        return arches;
    }
}


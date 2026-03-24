import * as THREE from 'three';

export interface PlacementBounds {
    minX: number;
    maxX: number;
    minZ: number;
    maxZ: number;
    minY: number;
    maxY: number;
}

export interface PlacementConfig {
    sceneSize: number;
    minDistanceToWall: number;
    minDistanceBetween: number;
    minHeight: number;
    maxHeight: number;
    seed?: number;
}

/** Размещение объектов в сцене с фильтрами коллизий. */
export class ObjectPlacer {
    private rng: () => number;
    private bounds: PlacementBounds;
    
    constructor(private config: PlacementConfig) {
        // Простой LCG генератор
        let seed = config.seed || Date.now();
        this.rng = () => {
            seed = (seed * 1103515245 + 12345) & 0x7fffffff;
            return seed / 0x7fffffff;
        };
        
        const half = config.sceneSize / 2;
        this.bounds = {
            minX: -half + config.minDistanceToWall,
            maxX: half - config.minDistanceToWall,
            minZ: -half + config.minDistanceToWall,
            maxZ: half - config.minDistanceToWall,
            minY: config.minHeight,
            maxY: config.maxHeight
        };
    }
    
    /** Разместить объекты с проверкой коллизий. */
    placeObjects(
        count: number,
        geometry: THREE.BufferGeometry,
        radius: number
    ): THREE.Vector3[] {
        const positions: THREE.Vector3[] = [];
        const attempts = count * 100; // Максимум попыток
        
        for (let i = 0; i < attempts && positions.length < count; i++) {
            const pos = this.generateRandomPosition();
            
            // Проверка расстояния до стен
            if (!this.isValidPosition(pos, radius)) {
                continue;
            }
            
            // Проверка расстояния до других объектов
            let tooClose = false;
            for (const existing of positions) {
                if (pos.distanceTo(existing) < this.config.minDistanceBetween) {
                    tooClose = true;
                    break;
                }
            }
            
            if (!tooClose) {
                positions.push(pos);
            }
        }
        
        return positions;
    }
    
    private generateRandomPosition(): THREE.Vector3 {
        return new THREE.Vector3(
            this.bounds.minX + (this.bounds.maxX - this.bounds.minX) * this.rng(),
            this.bounds.minY + (this.bounds.maxY - this.bounds.minY) * this.rng(),
            this.bounds.minZ + (this.bounds.maxZ - this.bounds.minZ) * this.rng()
        );
    }
    
    private isValidPosition(pos: THREE.Vector3, radius: number): boolean {
        // Проверка выхода за границы с учетом радиуса
        return (
            pos.x - radius >= this.bounds.minX &&
            pos.x + radius <= this.bounds.maxX &&
            pos.z - radius >= this.bounds.minZ &&
            pos.z + radius <= this.bounds.maxZ &&
            pos.y >= this.bounds.minY &&
            pos.y <= this.bounds.maxY
        );
    }
}


import * as THREE from 'three';

export interface HiddenCaster {
    id: string;
    mesh: THREE.Mesh;
    radius: number;
    found: boolean;
}

/** Система проверки попадания по объектам. */
export class HitTester {
    private raycaster: THREE.Raycaster;
    
    constructor() {
        this.raycaster = new THREE.Raycaster();
    }
    
    /** Попытка пометить объект по лучу из камеры. */
    tryMark(
        camera: THREE.Camera,
        casters: HiddenCaster[],
        maxDist: number = 25,
        tolerance: number = 0.6
    ): HiddenCaster | null {
        // Луч из центра экрана
        this.raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
        
        let closest: HiddenCaster | null = null;
        let closestDist = Infinity;
        
        for (const caster of casters) {
            if (caster.found) continue;
            
            // Получаем мировую позицию центра объекта
            const worldPos = new THREE.Vector3();
            caster.mesh.getWorldPosition(worldPos);
            
            // Расстояние от луча до центра объекта
            const distanceToRay = this.distanceToRay(
                this.raycaster.ray.origin,
                this.raycaster.ray.direction,
                worldPos
            );
            
            // Проверка попадания
            if (distanceToRay <= tolerance) {
                // Проверка, что объект перед камерой и в пределах maxDist
                const toObject = worldPos.clone().sub(this.raycaster.ray.origin);
                const alongRay = toObject.dot(this.raycaster.ray.direction);
                
                if (alongRay > 0 && alongRay <= maxDist) {
                    if (distanceToRay < closestDist) {
                        closestDist = distanceToRay;
                        closest = caster;
                    }
                }
            }
        }
        
        return closest;
    }
    
    /** Расстояние от точки до луча. */
    private distanceToRay(
        rayOrigin: THREE.Vector3,
        rayDir: THREE.Vector3,
        point: THREE.Vector3
    ): number {
        const toPoint = point.clone().sub(rayOrigin);
        const projection = toPoint.dot(rayDir);
        const projectedPoint = rayOrigin.clone().add(rayDir.clone().multiplyScalar(projection));
        return point.distanceTo(projectedPoint);
    }
}


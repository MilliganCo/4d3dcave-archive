import * as THREE from 'three';

/** Управление траекторией движения света. */
export class LightCurve {
    private curve: THREE.CatmullRomCurve3;
    private arcLengths: number[] = [];
    private totalLength: number = 0;
    private t: number = 0;
    private speed: number;
    private paused: boolean = false;
    private pauseTime: number = 0;
    private pauseDuration: number = 0;
    
    constructor(
        points: THREE.Vector3[],
        speed: number = 4.0,
        closed: boolean = false
    ) {
        this.curve = new THREE.CatmullRomCurve3(points, closed);
        this.speed = speed;
        this.precomputeArcLengths();
    }
    
    private precomputeArcLengths(): void {
        const segments = 1000;
        this.totalLength = this.curve.getLength();
        
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const length = this.curve.getLength(0, t);
            this.arcLengths.push(length);
        }
    }
    
    /** Обновление позиции вдоль кривой. */
    update(dt: number): void {
        if (this.paused) {
            this.pauseTime += dt;
            if (this.pauseTime >= this.pauseDuration) {
                this.paused = false;
                this.pauseTime = 0;
            }
            return;
        }
        
        // Движение по кривой с учетом скорости
        const distance = this.speed * dt;
        const deltaT = distance / this.totalLength;
        this.t = (this.t + deltaT) % 1.0;
    }
    
    /** Получить текущую позицию на кривой. */
    getPosition(): THREE.Vector3 {
        return this.curve.getPoint(this.t);
    }
    
    /** Получить направление (тангенс) в текущей точке. */
    getTangent(): THREE.Vector3 {
        return this.curve.getTangent(this.t).normalize();
    }
    
    /** Остановить свет на указанное время. */
    pause(duration: number): void {
        if (!this.paused) {
            this.paused = true;
            this.pauseDuration = duration;
            this.pauseTime = 0;
        }
    }
    
    isPaused(): boolean {
        return this.paused;
    }
    
    /** Сброс позиции. */
    reset(): void {
        this.t = 0;
        this.paused = false;
        this.pauseTime = 0;
    }
}


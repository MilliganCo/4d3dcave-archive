import { HiddenCaster } from '../core/hit';

/** Управление целями игры. */
export class Objectives {
    private targetCount: number;
    private foundCount: number = 0;
    private foundIds: Set<string> = new Set();
    
    constructor(targetCount: number) {
        this.targetCount = targetCount;
    }
    
    /** Пометка найденного объекта. */
    mark(caster: HiddenCaster): boolean {
        if (caster.found || this.foundIds.has(caster.id)) {
            return false;
        }
        
        caster.found = true;
        this.foundIds.add(caster.id);
        this.foundCount++;
        return true;
    }
    
    /** Проверка завершения. */
    completed(): boolean {
        return this.foundCount >= this.targetCount;
    }
    
    getFoundCount(): number {
        return this.foundCount;
    }
    
    getTargetCount(): number {
        return this.targetCount;
    }
    
    reset(): void {
        this.foundCount = 0;
        this.foundIds.clear();
    }
}


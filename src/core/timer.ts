/** Таймер игры. */
export class GameTimer {
    private startTime: number = 0;
    private elapsed: number = 0;
    private running: boolean = false;
    
    start(): void {
        this.startTime = performance.now();
        this.running = true;
    }
    
    stop(): void {
        if (this.running) {
            this.elapsed += performance.now() - this.startTime;
            this.running = false;
        }
    }
    
    reset(): void {
        this.startTime = 0;
        this.elapsed = 0;
        this.running = false;
    }
    
    getElapsed(): number {
        if (this.running) {
            return this.elapsed + (performance.now() - this.startTime);
        }
        return this.elapsed;
    }
    
    getFormatted(): string {
        const totalSeconds = Math.floor(this.getElapsed() / 1000);
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    isRunning(): boolean {
        return this.running;
    }
}


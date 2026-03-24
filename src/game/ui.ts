/** Управление UI. */
export class UIManager {
    private menuEl: HTMLElement;
    private hudEl: HTMLElement;
    private victoryEl: HTMLElement;
    private startBtn: HTMLElement;
    private resetBtn: HTMLElement;
    private restartBtn: HTMLElement;
    private difficultySelect: HTMLSelectElement;
    private foundCountEl: HTMLElement;
    private totalCountEl: HTMLElement;
    private timerEl: HTMLElement;
    private cooldownInfoEl: HTMLElement;
    private cooldownTimerEl: HTMLElement;
    private victoryTimeEl: HTMLElement;
    
    constructor() {
        this.menuEl = document.getElementById('menu')!;
        this.hudEl = document.getElementById('hud')!;
        this.victoryEl = document.getElementById('victory')!;
        this.startBtn = document.getElementById('start-btn')!;
        this.resetBtn = document.getElementById('reset-btn')!;
        this.restartBtn = document.getElementById('restart-btn')!;
        this.difficultySelect = document.getElementById('difficulty-select') as HTMLSelectElement;
        this.foundCountEl = document.getElementById('found-count')!;
        this.totalCountEl = document.getElementById('total-count')!;
        this.timerEl = document.getElementById('timer')!;
        this.cooldownInfoEl = document.getElementById('cooldown-info')!;
        this.cooldownTimerEl = document.getElementById('cooldown-timer')!;
        this.victoryTimeEl = document.getElementById('victory-time')!;
    }
    
    showMenu(): void {
        this.menuEl.classList.remove('hidden');
        this.hudEl.classList.add('hidden');
        this.victoryEl.classList.add('hidden');
    }
    
    showHUD(): void {
        this.menuEl.classList.add('hidden');
        this.hudEl.classList.remove('hidden');
        this.victoryEl.classList.add('hidden');
    }
    
    showVictory(): void {
        this.menuEl.classList.add('hidden');
        this.hudEl.classList.add('hidden');
        this.victoryEl.classList.remove('hidden');
    }
    
    updateFoundCount(found: number, total: number): void {
        this.foundCountEl.textContent = found.toString();
        this.totalCountEl.textContent = total.toString();
    }
    
    updateTimer(time: string): void {
        this.timerEl.textContent = time;
    }
    
    updateCooldown(remaining: number): void {
        if (remaining > 0) {
            this.cooldownInfoEl.classList.remove('hidden');
            this.cooldownTimerEl.textContent = Math.ceil(remaining).toString();
        } else {
            this.cooldownInfoEl.classList.add('hidden');
        }
    }
    
    setVictoryTime(time: string): void {
        this.victoryTimeEl.textContent = time;
    }
    
    getDifficulty(): 'easy' | 'normal' | 'hard' {
        return this.difficultySelect.value as 'easy' | 'normal' | 'hard';
    }
    
    onStart(callback: () => void): void {
        this.startBtn.addEventListener('click', callback);
    }
    
    onReset(callback: () => void): void {
        this.resetBtn.addEventListener('click', callback);
    }
    
    onRestart(callback: () => void): void {
        this.restartBtn.addEventListener('click', callback);
    }
}


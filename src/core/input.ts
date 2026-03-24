/** Обработка ввода. */
export class InputManager {
    private keys: Set<string> = new Set();
    private mouseButtons: Set<number> = new Set();
    private mouseDelta: { x: number; y: number } = { x: 0, y: 0 };
    private lastMousePos: { x: number; y: number } = { x: 0, y: 0 };
    
    constructor(private canvas: HTMLCanvasElement) {
        this.setupListeners();
    }
    
    private setupListeners(): void {
        window.addEventListener('keydown', (e) => {
            this.keys.add(e.code);
        });
        
        window.addEventListener('keyup', (e) => {
            this.keys.delete(e.code);
        });
        
        this.canvas.addEventListener('mousedown', (e) => {
            this.mouseButtons.add(e.button);
        });
        
        this.canvas.addEventListener('mouseup', (e) => {
            this.mouseButtons.delete(e.button);
        });
        
        // PointerLockControls обрабатывает движение мыши сам,
        // но мы можем отслеживать для других целей
        this.canvas.addEventListener('mousemove', (e) => {
            if (document.pointerLockElement === this.canvas && e.movementX !== undefined) {
                this.mouseDelta.x += e.movementX;
                this.mouseDelta.y += e.movementY;
            }
        });
    }
    
    isKeyPressed(code: string): boolean {
        return this.keys.has(code);
    }
    
    isMouseButtonPressed(button: number): boolean {
        return this.mouseButtons.has(button);
    }
    
    getMouseDelta(): { x: number; y: number } {
        const delta = { ...this.mouseDelta };
        this.mouseDelta = { x: 0, y: 0 };
        return delta;
    }
    
    requestPointerLock(): void {
        this.canvas.requestPointerLock();
    }
}


import * as THREE from 'three';
import { PointerLockControls } from 'three/examples/jsm/controls/PointerLockControls.js';
import Stats from 'stats.js';

import { InputManager } from './core/input';
import { HitTester, HiddenCaster } from './core/hit';
import { GameTimer } from './core/timer';
import { ObjectPlacer } from './core/placement';
import { SceneBuilder } from './render/scene';
import { enableShadows } from './render/shadows';
import { PostProcessor } from './render/post';
import { World, WorldConfig } from './game/world';
import { Objectives } from './game/objectives';
import { UIManager } from './game/ui';

const DIFFICULTY_TARGETS = {
    easy: 7,
    normal: 10,
    hard: 13
};

const CFG: WorldConfig = {
    sceneSize: 80,
    difficulty: 'normal',
    shadowQuality: 'med',
    lightSpeed: 4.0,
    lightPauseDuration: 3.0,
    lightCooldown: 10.0,
    hitMaxDist: 25,
    hitTolerance: 0.6
};

class Game {
    private renderer: THREE.WebGLRenderer;
    private camera: THREE.PerspectiveCamera;
    private controls: PointerLockControls;
    private input: InputManager;
    private hitTester: HitTester;
    private timer: GameTimer;
    private world: World;
    private objectives: Objectives;
    private ui: UIManager;
    private sceneBuilder: SceneBuilder;
    private postProcessor: PostProcessor;
    private stats: Stats;
    
    private lightCooldown: number = 0;
    private playing: boolean = false;
    
    constructor() {
        // Canvas
        const canvas = document.getElementById('canvas') as HTMLCanvasElement;
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ 
            canvas,
            antialias: true 
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Включение теней
        enableShadows(this.renderer, CFG.shadowQuality);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            100
        );
        this.camera.position.set(0, 2, 5);
        
        // Controls (PointerLockControls управляет камерой напрямую)
        this.controls = new PointerLockControls(this.camera, canvas);
        
        // Input
        this.input = new InputManager(canvas);
        
        // Hit tester
        this.hitTester = new HitTester();
        
        // Timer
        this.timer = new GameTimer();
        
        // UI
        this.ui = new UIManager();
        this.setupUI();
        
        // World
        this.world = new World(CFG);
        
        // Scene builder
        this.sceneBuilder = new SceneBuilder(this.world.scene);
        
        // Post processor
        this.postProcessor = new PostProcessor();
        
        // Stats (dev)
        this.stats = new Stats();
        this.stats.showPanel(0);
        document.body.appendChild(this.stats.dom);
        
        // Resize handler
        window.addEventListener('resize', () => this.onResize());
        
        // ESC для выхода из pointer lock
        document.addEventListener('pointerlockchange', () => {
            if (document.pointerLockElement !== canvas) {
                this.ui.showMenu();
                this.playing = false;
            } else {
                // Pointer lock активирован - можно играть
                if (this.world.receivers.length > 0) {
                    this.playing = true;
                    this.lastTime = 0;
                    requestAnimationFrame((t) => this.animate(t));
                }
            }
        });
        
        // Запуск анимации (рендер будет происходить всегда)
        this.lastTime = 0;
        requestAnimationFrame((t) => this.animate(t));
    }
    
    private setupUI(): void {
        this.ui.onStart(() => this.startGame());
        this.ui.onReset(() => this.resetGame());
        this.ui.onRestart(() => this.restartGame());
    }
    
    private startGame(): void {
        const difficulty = this.ui.getDifficulty();
        CFG.difficulty = difficulty;
        
        // Построение сцены
        this.world.receivers = this.sceneBuilder.buildReceivers(CFG.sceneSize);
        
        // Размещение скрытых объектов
        this.placeCasters();
        
        // Создание objectives
        const targetCount = DIFFICULTY_TARGETS[difficulty];
        this.objectives = new Objectives(targetCount);
        
        // Обновление UI
        this.ui.updateFoundCount(0, targetCount);
        this.ui.showHUD();
        
        // Запуск игры
        this.timer.start();
        this.world.reset();
        this.lastTime = 0;
        
        // Сброс позиции камеры
        this.camera.position.set(0, 2, 5);
        this.camera.rotation.set(0, 0, 0);
        
        // Захват мыши (анимация запустится автоматически при активации pointer lock)
        this.input.requestPointerLock();
    }
    
    private placeCasters(): void {
        const difficulty = CFG.difficulty;
        const targetCount = DIFFICULTY_TARGETS[difficulty];
        
        // Геометрии для объектов
        const geometries = [
            new THREE.BoxGeometry(1, 1, 1),
            new THREE.SphereGeometry(0.5, 16, 16),
            new THREE.ConeGeometry(0.5, 1.5, 8),
            new THREE.TorusGeometry(0.4, 0.2, 8, 16),
            new THREE.CylinderGeometry(0.4, 0.4, 1.2, 8),
        ];
        
        // Плейсер
        const placer = new ObjectPlacer({
            sceneSize: CFG.sceneSize,
            minDistanceToWall: 1.0,
            minDistanceBetween: 2.5,
            minHeight: 0.5,
            maxHeight: 3.0,
            seed: Date.now()
        });
        
        // Размещаем объекты
        const positions = placer.placeObjects(
            targetCount + 5, // Немного больше для разнообразия
            geometries[0],
            0.5
        );
        
        // Создаем скрытые кастеры
        this.world.casters = [];
        for (let i = 0; i < targetCount; i++) {
            const pos = positions[i];
            const geom = geometries[i % geometries.length];
            
            // Материал для невидимого объекта
            const material = new THREE.MeshBasicMaterial({
                color: 0x000000,
                transparent: true,
                opacity: 0
            });
            (material as any).colorWrite = false;
            material.depthWrite = false;
            
            const mesh = new THREE.Mesh(geom, material);
            mesh.position.copy(pos);
            mesh.castShadow = true;
            mesh.receiveShadow = false;
            mesh.visible = true; // Важно: visible=true для рейкаста
            
            const caster: HiddenCaster = {
                id: `caster_${i}`,
                mesh,
                radius: 0.6,
                found: false
            };
            
            this.world.scene.add(mesh);
            this.world.casters.push(caster);
        }
    }
    
    private resetGame(): void {
        this.playing = false;
        this.timer.stop();
        this.timer.reset();
        this.world.reset();
        this.lightCooldown = 0;
        
        // Очистка сцены
        while (this.world.scene.children.length > 0) {
            const obj = this.world.scene.children[0];
            this.world.scene.remove(obj);
            if (obj instanceof THREE.Mesh) {
                obj.geometry.dispose();
                if (obj.material instanceof THREE.Material) {
                    obj.material.dispose();
                }
            }
        }
        
        this.ui.showMenu();
    }
    
    private restartGame(): void {
        this.resetGame();
        setTimeout(() => this.startGame(), 100);
    }
    
    private handleInput(dt: number): void {
        if (!this.playing || document.pointerLockElement !== this.renderer.domElement) return;
        
        // Поворот камеры через PointerLockControls (используется движение мыши)
        // PointerLockControls автоматически обрабатывает movementX/Y через события
        
        // Движение
        const velocity = new THREE.Vector3();
        if (this.input.isKeyPressed('KeyW')) velocity.z -= 1;
        if (this.input.isKeyPressed('KeyS')) velocity.z += 1;
        if (this.input.isKeyPressed('KeyA')) velocity.x -= 1;
        if (this.input.isKeyPressed('KeyD')) velocity.x += 1;
        
        if (velocity.length() > 0) {
            velocity.normalize();
            velocity.multiplyScalar(4 * dt); // Скорость движения
            
            this.controls.moveRight(velocity.x);
            this.controls.moveForward(velocity.z);
        }
        
        // Прыжок (упрощенная реализация)
        if (this.input.isKeyPressed('Space')) {
            // Простая реализация прыжка
        }
        
        // Стоп света
        if (this.input.isKeyPressed('ShiftLeft') || this.input.isKeyPressed('ShiftRight')) {
            if (this.lightCooldown <= 0 && !this.world.isLightPaused()) {
                this.world.pauseLight(CFG.lightPauseDuration);
                this.lightCooldown = CFG.lightCooldown;
            }
        }
        
        // Обновление кулдауна
        if (this.lightCooldown > 0) {
            this.lightCooldown -= dt;
            this.ui.updateCooldown(this.lightCooldown);
        }
        
        // Пометка объекта
        if (this.input.isMouseButtonPressed(0)) {
            const hit = this.hitTester.tryMark(
                this.camera,
                this.world.casters,
                CFG.hitMaxDist,
                CFG.hitTolerance
            );
            
            if (hit) {
                if (this.objectives.mark(hit)) {
                    // Визуальная обратная связь
                    this.showFoundEffect(hit);
                    this.ui.updateFoundCount(
                        this.objectives.getFoundCount(),
                        this.objectives.getTargetCount()
                    );
                    
                    // Проверка победы
                    if (this.objectives.completed()) {
                        this.victory();
                    }
                }
            }
        }
    }
    
    private showFoundEffect(caster: HiddenCaster): void {
        // Кратковременная вспышка силуэта
        const originalMat = caster.mesh.material as THREE.MeshBasicMaterial;
        const flashMat = new THREE.MeshBasicMaterial({
            color: 0x4a9eff,
            transparent: true,
            opacity: 0.3
        });
        
        caster.mesh.material = flashMat;
        
        setTimeout(() => {
            caster.mesh.material = originalMat;
            flashMat.dispose();
        }, 500);
    }
    
    private victory(): void {
        this.playing = false;
        this.timer.stop();
        this.ui.setVictoryTime(this.timer.getFormatted());
        this.ui.showVictory();
    }
    
    private lastTime: number = 0;
    
    private animate(currentTime: number = 0): void {
        this.stats.begin();
        
        // Вычисление delta time
        const dt = this.lastTime > 0 ? (currentTime - this.lastTime) / 1000 : 0.016;
        this.lastTime = currentTime;
        const clampedDt = Math.min(dt, 0.033); // Ограничение максимального dt
        
        if (this.playing) {
            // Обновление мира
            this.world.update(clampedDt);
            
            // Обработка ввода
            this.handleInput(clampedDt);
            
            // Обновление таймера
            this.ui.updateTimer(this.timer.getFormatted());
        }
        
        // Рендер всегда (даже если игра не запущена)
        this.postProcessor.render(this.renderer, this.world.scene, this.camera);
        
        this.stats.end();
        
        requestAnimationFrame((t) => this.animate(t));
    }
    
    private onResize(): void {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
}

// Запуск игры
const game = new Game();


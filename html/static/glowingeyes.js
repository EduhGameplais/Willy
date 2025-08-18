/*Code by Kaykk11*/

class GlowingEyes {
    constructor() {
        this.leftEye = document.getElementById('leftEye');
        this.rightEye = document.getElementById('rightEye');
        this.shapeButtons = document.querySelectorAll('.shape-btn');
        
        this.currentShape = 'square';
        this.isAutoBlinking = false;
        this.autoBlinkInterval = null;
        this.shapes = ['square', 'happiness', 'sadness', 'angry', 'thinking', 'listening'];
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.startAutoBlink();
        this.startPulseEffect();
        this.addTouchSupport();
        this.addKeyboardSupport();
        this.startRandomLook();

        this.changeShape('square');
        this.setActiveButton('square');
    }
    
    setupEventListeners() {
        this.shapeButtons.forEach((btn, index) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const shape = this.shapes[index];
                this.changeShape(shape);
                this.setActiveButton(shape);
            });
        });
        
        this.leftEye.addEventListener('click', () => this.manualBlink());
        this.rightEye.addEventListener('click', () => this.manualBlink());
    }
    
    addKeyboardSupport() {
        document.addEventListener('keydown', (e) => {
            const num = parseInt(e.key);
            if (num >= 1 && num <= 6) {
                const shape = this.shapes[num - 1];
                this.changeShape(shape);
                this.setActiveButton(shape);
            }
            
            if (e.code === 'Space' || e.code === 'Enter') {
                e.preventDefault();
                this.manualBlink();
            }
        });
    }
    
    changeShape(shape) {
        this.shapes.forEach(s => {
            this.leftEye.classList.remove(s);
            this.rightEye.classList.remove(s);
        });
        
        this.leftEye.className = 'eye left-eye';
        this.rightEye.className = 'eye right-eye';
        
        this.leftEye.classList.add(shape);
        this.rightEye.classList.add(shape);
        this.currentShape = shape;
        
        this.restartPulseEffect();
    }
    
    setActiveButton(shape) {
        this.shapeButtons.forEach(btn => btn.classList.remove('active'));
        const index = this.shapes.indexOf(shape);
        if (index >= 0) {
            this.shapeButtons[index].classList.add('active');
        }
    }
    
    manualBlink() {
        this.stopAutoBlink();
        this.leftEye.classList.add('blinking');
        this.rightEye.classList.add('blinking');
        
        setTimeout(() => {
            this.leftEye.classList.remove('blinking');
            this.rightEye.classList.remove('blinking');
            setTimeout(() => this.startAutoBlink(), 3000);
        }, 600);
        
        if (navigator.vibrate) {
            navigator.vibrate(30);
        }
    }
    
    startAutoBlink() {
        if (this.autoBlinkInterval) return;
        this.isAutoBlinking = true;
        
        this.autoBlinkInterval = setInterval(() => {
            if (this.isAutoBlinking) {
                const delay = Math.random() * 3000 + 2000;
                setTimeout(() => {
                    if (this.isAutoBlinking) {
                        this.leftEye.classList.add('blinking');
                        this.rightEye.classList.add('blinking');
                        setTimeout(() => {
                            this.leftEye.classList.remove('blinking');
                            this.rightEye.classList.remove('blinking');
                        }, 600);
                    }
                }, delay);
            }
        }, 5000);
    }
    
    stopAutoBlink() {
        if (this.autoBlinkInterval) {
            clearInterval(this.autoBlinkInterval);
            this.autoBlinkInterval = null;
        }
        this.isAutoBlinking = false;
    }
    
    startPulseEffect() {
        this.leftEye.classList.add('pulsing');
        this.rightEye.classList.add('pulsing');
    }
    
    restartPulseEffect() {
        this.leftEye.classList.remove('pulsing');
        this.rightEye.classList.remove('pulsing');
        
        setTimeout(() => {
            this.leftEye.classList.add('pulsing');
            this.rightEye.classList.add('pulsing');
        }, 50);
    }
    
    addTouchSupport() {
        document.addEventListener('touchstart', (e) => {
            if (e.touches.length > 1) {
                e.preventDefault();
            }
        }, { passive: false });
        
        let startX = 0;
        let startY = 0;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const dx = endX - startX;
            const dy = endY - startY;
            
            if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > 50) {
                const currentIndex = this.shapes.indexOf(this.currentShape);
                let nextIndex;
                
                if (dx > 0 && currentIndex < this.shapes.length - 1) {
                    nextIndex = currentIndex + 1;
                } else if (dx < 0 && currentIndex > 0) {
                    nextIndex = currentIndex - 1;
                }
                
                if (nextIndex !== undefined) {
                    const nextShape = this.shapes[nextIndex];
                    this.changeShape(nextShape);
                    this.setActiveButton(nextShape);
                }
            }
        }, { passive: true });
    }
    
    setEmotion(emotion) {
        if (this.shapes.includes(emotion)) {
            this.changeShape(emotion);
            this.setActiveButton(emotion);
        }
    }
    
    getCurrentEmotion() {
        return this.currentShape;
    }

    startRandomLook() {
        setInterval(() => {
            this.performLookSequence();
        }, 7000);
    }

    performLookSequence() {
        const lookPatterns = [
            ['look-left', 'look-right'],           
            ['look-right', 'look-left'],           
            ['look-left', 'look-right', 'look-left'],
            ['look-right', 'look-left', 'look-right'],
            ['look-left'],                         
            ['look-right'],                       
        ];

        const selectedPattern = lookPatterns[Math.floor(Math.random() * lookPatterns.length)];
        
        this.executeLookPattern(selectedPattern, 0);
    }

    executeLookPattern(pattern, index) {
        if (index >= pattern.length) return;

        const direction = pattern[index];
        
        this.leftEye.classList.add('look-side', direction);
        this.rightEye.classList.add('look-side', direction);

        setTimeout(() => {
            this.leftEye.classList.remove('look-side', 'look-left', 'look-right');
            this.rightEye.classList.remove('look-side', 'look-left', 'look-right');
            
            if (index + 1 < pattern.length) {
                setTimeout(() => {
                    this.executeLookPattern(pattern, index + 1);
                }, 500);
            }
        }, 2000);
    }
}
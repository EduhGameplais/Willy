let mouthAnimation = null;
let blinkingInterval = null;
let currentState = 'idle';

const status = document.getElementById('status');
const thinkingBubble = document.getElementById('thinkingBubble');
const happyBubble = document.getElementById('happyBubble');
const romanticBubble = document.getElementById('romanticBubble');

function blinkBothEyes() {
    const eyes = document.querySelectorAll('.eye');
    eyes.forEach(eye => eye.classList.add('blinking'));
    setTimeout(() => {
        eyes.forEach(eye => eye.classList.remove('blinking'));
    }, 120);
}

function startBlinking() {
    if (blinkingInterval) clearInterval(blinkingInterval);
    blinkingInterval = setInterval(() => {
        blinkBothEyes();
    }, 2000 + Math.random() * 1000);
}

function startMouthAnimation() {
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        bar.classList.remove('idle', 'thinking', 'happy', 'romantic');
        bar.classList.add('speaking');
    });
    
    if (mouthAnimation) clearInterval(mouthAnimation);
    mouthAnimation = setInterval(() => {
        bars.forEach((bar, index) => {
            const randomHeight = 15 + Math.random() * 35;
            bar.style.height = randomHeight + 'px';
            setTimeout(() => {
                const randomHeight2 = 20 + Math.random() * 25;
                bar.style.height = randomHeight2 + 'px';
            }, 50 + index * 10);
        });
    }, 100);
}

function stopMouthAnimation() {
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        bar.classList.remove('speaking');
        bar.classList.add('idle');
        bar.style.height = '20px';
    });
    if (mouthAnimation) {
        clearInterval(mouthAnimation);
        mouthAnimation = null;
    }
}

function hideAllBubbles() {
    if (thinkingBubble) thinkingBubble.classList.remove('show');
    if (happyBubble) happyBubble.classList.remove('show');
    if (romanticBubble) romanticBubble.classList.remove('show');
}

function startThinking() {
    currentState = 'thinking';
    const eyes = document.querySelectorAll('.eye');
    const bars = document.querySelectorAll('.bar');
    
    stopMouthAnimation();
    
    if (blinkingInterval) {
        clearInterval(blinkingInterval);
        blinkingInterval = null;
    }
    
    hideAllBubbles();
    
    eyes.forEach(eye => {
        eye.className = 'eye thinking';
    });
    
    bars.forEach(bar => {
        bar.className = 'bar thinking';
    });
    
    if (thinkingBubble) {
        thinkingBubble.classList.add('show');
    }
    
    if (status) {
        status.textContent = 'Estado: Pensando... 🤔';
    }
}

function startHappy() {
    currentState = 'happy';
    const eyes = document.querySelectorAll('.eye');
    const bars = document.querySelectorAll('.bar');
    
    stopMouthAnimation();
    hideAllBubbles();
    
    eyes.forEach(eye => {
        eye.className = 'eye happy';
    });
    
    bars.forEach(bar => {
        bar.className = 'bar happy';
    });
    
    if (happyBubble) {
        happyBubble.classList.add('show');
    }
    
    startBlinking();
    
    if (status) {
        status.textContent = 'Estado: Feliz! 😊';
    }
}

function startRomantic() {
    currentState = 'romantic';
    const eyes = document.querySelectorAll('.eye');
    const bars = document.querySelectorAll('.bar');
    
    stopMouthAnimation();
    hideAllBubbles();
    
    eyes.forEach(eye => {
        eye.className = 'eye romantic';
    });
    
    bars.forEach(bar => {
        bar.className = 'bar romantic';
    });
    
    if (romanticBubble) {
        romanticBubble.classList.add('show');
    }
    
    startBlinking();
    
    if (status) {
        status.textContent = 'Estado: Romântico 💕';
    }
}

function stopThinking() {
    if (currentState !== 'thinking') return;
    
    const eyes = document.querySelectorAll('.eye');
    const bars = document.querySelectorAll('.bar');
    
    eyes.forEach(eye => {
        eye.className = 'eye normal';
    });
    
    bars.forEach(bar => {
        bar.className = 'bar idle';
        bar.style.height = '20px';
    });
    
    hideAllBubbles();
    
    startBlinking();
    currentState = 'idle';
    
    if (status) {
        status.textContent = 'Estado: Idle';
    }
}

function setIdleState() {
    currentState = 'idle';
    const eyes = document.querySelectorAll('.eye');
    const bars = document.querySelectorAll('.bar');
    
    stopMouthAnimation();
    hideAllBubbles();
    
    eyes.forEach(eye => {
        eye.className = 'eye normal';
    });
    
    bars.forEach(bar => {
        bar.className = 'bar idle';
        bar.style.height = '20px';
    });
    
    startBlinking();
    
    if (status) {
        status.textContent = 'Estado: Idle';
    }
}

function setState(state) {
    switch(state) {
        case 'idle':
            setIdleState();
            break;
        case 'thinking':
            startThinking();
            break;
        case 'happy':
            startHappy();
            break;
        case 'romantic':
            startRomantic();
            break;
        case 'speaking':
            stopThinking();
            currentState = 'speaking';
            const eyes = document.querySelectorAll('.eye');
            eyes.forEach(eye => eye.className = 'eye normal');
            hideAllBubbles();
            startMouthAnimation();
            startBlinking();
            if (status) {
                status.textContent = 'Estado: Falando 🎵';
            }
            break;
    }
}

window.robotFace = {
    startSpeaking: () => {
        stopThinking();
        currentState = 'speaking';
        const eyes = document.querySelectorAll('.eye');
        eyes.forEach(eye => eye.className = 'eye normal');
        hideAllBubbles();
        startMouthAnimation();
        startBlinking();
        if (status) {
            status.textContent = 'Estado: Falando 🎵';
        }
    },
    
    stopSpeaking: () => {
        if (currentState === 'speaking') {
            setIdleState();
        }
    },
    
    blink: blinkBothEyes,
    
    startThinking: startThinking,
    stopThinking: stopThinking,
    setIdle: setIdleState,
    setHappy: startHappy,
    setRomantic: startRomantic
};

document.addEventListener('DOMContentLoaded', function() {
    setIdleState();
});

function demoSequence() {
    setIdleState();
    setTimeout(() => startThinking(), 3000);
    setTimeout(() => startHappy(), 6000);
    setTimeout(() => startRomantic(), 9000);
    setTimeout(() => setState('speaking'), 12000);
    setTimeout(() => setIdleState(), 15000);
    setTimeout(demoSequence, 18000);
}

setTimeout(demoSequence, 3000);
let mouthAnimation = null;
let blinkingInterval = null;
let currentState = 'idle';

const status = document.getElementById('status');
const thinkingBubble = document.getElementById('thinkingBubble');

function blinkBothEyes() {
  const eyes = document.querySelectionAll('.eye');
  eyes.forEach(eye => eye.classList.add('bliking'));
  setTimeout(() => {
    eyes.forEach(eye => eye.classlist.remove('bliking'));
    }, 120);
}

function startBlinking() {
  if (blinkingInterval) clearInterval(blinkingInterval);
  blinkingInterval = setInterval(() => {
    blinkBothEyes();
  }, 2000 + Math.random() *1000);
}

function startMouthAnimation() {
  const bars = document.querySelectorAll('.bar');
  bars.forEach(bar => {
    bar.classList.remove('idle', 'thinking');
    bar.classList.add('speaking');
  });

  if (mouthAnimation) clearInterval(mouthAnimation)
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
 
function startBlinking() {
  currentState = 'thinking';
  const eyes = document.querySelectorAll('.eye');
  const bars = document.querySelectorAll('.bar');

  stopMouthAnimation();

  if (blinkingInterval) {
    clearInterval(blinkingInterval);
    blinkingInterval = null;
  }

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


function stopThinking() {
  if (currentState  !== 'thinking') return;

  const eyes = document.querySelectorAll('.eye');
  const bars = document.querySelectorAll('.bar');

  eyes.forEach(eye => {
    eye.className = 'eye normal';
  });

  bars.forEach(bar => {
    bar.className = 'bar idle';
    bar.style.height = '20px';
    });

  if (thinkingBubble) {
    thinkingBubble.classList.remove('show');
  };

  startBlinking();
  currentState = 'idle';

  if (status) {
    status.textContent = 'Estado idle';
  }
}

function setIdleState() {
  currentState = 'idle';
  const eyes = document.querySelectorAll('.eye');
  const eyes = document.querySelectorAll('.bar');
}
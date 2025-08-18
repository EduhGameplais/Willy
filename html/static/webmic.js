//Do chatinho Gepetinho.

let ws;
let audioContext;
let processor;
let micStream;
let buffer = [];

function floatTo16BitPCM(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++, offset += 2) {
        let s = Math.max(-1, Math.min(1, float32Array[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    return buffer;
}

function sendBufferedSamples(samplesNeeded) {
    while (buffer.length >= samplesNeeded) {
        const frame = buffer.splice(0, samplesNeeded);
        const pcmBuffer = floatTo16BitPCM(new Float32Array(frame));
        if (ws.readyState === WebSocket.OPEN) {
            ws.send(pcmBuffer);
        }
    }
}

async function startWebMic(ip, port, numberOfSamples) {
    audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
    await audioContext.resume();

   micStream = await navigator.mediaDevices.getUserMedia({
        audio: {
            channelCount: 1,
            noiseSuppression: false, // desligar
            echoCancellation: false, // desligar
            autoGainControl: true   // desligar
        }
    });

    ws = new WebSocket(`wss://${ip}:${port}`);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
        console.log("Conetado");

        const source = audioContext.createMediaStreamSource(micStream);
        processor = audioContext.createScriptProcessor(1024, 1, 1);

        processor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            buffer.push(...inputData);
            sendBufferedSamples(numberOfSamples);
            console.log("Conetado");
        };

        source.connect(processor);
        processor.connect(audioContext.destination);
    };
};

async function stopWebMic() {
    if (processor) processor.disconnect();
    if (audioContext) audioContext.close();
    if (micStream) micStream.getTracks().forEach(track => track.stop());
    if (ws && ws.readyState === WebSocket.OPEN) ws.close();
};
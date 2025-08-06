import numpy as np
from voice_recorder import listen
from function_manager import scan_functions
from faster_whisper import WhisperModel

scan_functions()
'''
audio = listen(3, 0.5, True)

model_size = "medium"

audio_np = np.frombuffer(b''.join(audio), dtype=np.int16).astype(np.float32) / 32768.0  # normaliza para -1.0 a 1.0

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")

segments, info = model.transcribe(audio_np, beam_size=5, language="pt")

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))'''
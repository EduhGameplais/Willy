import time
from faster_whisper import WhisperModel
import numpy as np

class Transcriber:
    def __init__(self, whisper_model: str, device: str = "cuda", compute_type="int8_float16"):
        start_time = time.perf_counter()
        self.model = WhisperModel(whisper_model, device="cuda", compute_type=compute_type)
        end_time = time.perf_counter()
        print(f"Whisper loaded. ({end_time-start_time})")

    def transcribe(self, audio: list[int]):
        audio_np = np.frombuffer(b''.join(audio), dtype=np.int16).astype(np.float32) / 32768.0  # normaliza para -1.0 a 1.0
        
        segments, info = self.model.transcribe(audio_np, beam_size=5, language="pt")
        
        print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
        
        full_text = ""
        
        for segment in segments:
            full_text += segment.text
            
        return full_text
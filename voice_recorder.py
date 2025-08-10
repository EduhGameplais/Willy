import time
import pyaudio
import numpy as np

from voice.silero import Silero

class VoiceRecorder:
    def __init__(self, silence_limit_secs: float, silero_threshold: float):
        self.vad = Silero()
        self.silence_limit_secs = silence_limit_secs
        self.silero_threshold = silero_threshold

    def listen(self, ): 
        """
        Grava voz até silencio ultrapassar o limite de silencio.
        
        Retorna: 
          - Audio bruto
          - Audio apenas voz detectada pelo VAD
        """
        
        audio = pyaudio.PyAudio()

        stream = audio.open(rate=16000, channels=1, format=pyaudio.paInt16, frames_per_buffer=1024, input=True)

        data: list[bytes] = []

        only_voice_data: list[bytes] = []

        num_samples = 512

        continue_recording = True

        last_voice_detected = time.perf_counter()

        i = 0
        print("Recording...")
        while continue_recording:
            audio_chunk = stream.read(num_samples)

            data.append(audio_chunk)

            new_confidence = self.vad.process_audio_chunk(audio_chunk)

            if new_confidence > self.silero_threshold:
                last_voice_detected = time.perf_counter()
                only_voice_data.append(audio_chunk)

            if time.perf_counter() - last_voice_detected > self.silence_limit_secs:
                continue_recording = False

            #print(new_confidence)
            #print(new_confidence > silero_threshold)
        print("Recording finished.")

        return data, only_voice_data
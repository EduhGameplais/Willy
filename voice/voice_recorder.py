import time
from typing import AsyncGenerator
import pyaudio
import numpy as np

from voice.audio_stream import AudioChunk, AudioFormat, AudioStream
from voice.silero import Silero

class SileroVoiceRecorder:
    """
    Gravador de voz com stop automatico usando Silero VAD.
    """
    def __init__(self, silence_limit_secs: float, silero_threshold: float):
        self.vad = Silero()
        self.silence_limit_secs = silence_limit_secs
        self.silero_threshold = silero_threshold

    def listen(self, stream: AudioStream): 
        """
        Grava voz até silêncio detectado ultrapassar o limite.
        """
        data = bytearray()
        only_voice_data = bytearray() ##TODO: Por algum motivo está bugado e não o áudio corretamente.
        last_voice_detected = time.perf_counter()

        print("Recording...")

        for chunk in stream.get_audio_chunks_streaming():
            audio_chunk = chunk.get_as("bytes")
            data.extend(audio_chunk)

            new_confidence = self.vad.process_audio_chunk(audio_chunk)

            print(new_confidence)
            
            if new_confidence > self.silero_threshold:
                
                last_voice_detected = time.perf_counter()
                only_voice_data.extend(audio_chunk)
                
            if time.perf_counter() - last_voice_detected > self.silence_limit_secs:
                if len(only_voice_data) == 0:
                    only_voice_data = data
                return AudioChunk(bytes(data), AudioFormat(16000, "int16")), AudioChunk(bytes(only_voice_data), AudioFormat(16000, "int16"))
                
        print("Recording finished.")
        return AudioChunk(bytes(data), AudioFormat(16000, "int16")), AudioChunk(bytes(only_voice_data), AudioFormat(16000, "int16"))
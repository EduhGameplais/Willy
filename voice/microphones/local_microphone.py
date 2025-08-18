import threading
import pyaudio
from voice.microphone import Microphone
from voice.audio_stream import AudioStream, AudioFormat, AudioChunk
import numpy as np

class LocalMicrophone(Microphone):
    def __init__(self, num_frames: int = 1536, audio_format: AudioFormat = AudioFormat(sample_rate=48000, format="float32")):
        self.num_frames = num_frames
        self.audio_format = audio_format

        # Cria PyAudio stream
        audio = pyaudio.PyAudio()
        self._stream = audio.open(
            rate=audio_format.sample_rate,
            channels=1,
            format=pyaudio.paFloat32 if audio_format.format == "float32" else pyaudio.paInt16,
            input=True,
            frames_per_buffer=num_frames
        )

        # Cria AudioStream
        self.audio_stream = AudioStream()
        self._running = False

    def start(self):
        """
        Inicia a captura em outra thread e retorna o AudioStream.
        """
        self._running = True
        threading.Thread(target=self.__capture_loop, daemon=True).start()
        return self.audio_stream

    def stop(self):
        self._running = False
        self._stream.stop_stream()
        self._stream.close()

    def __capture_loop(self):
        while self._running:
            raw = self._stream.read(self.num_frames, exception_on_overflow=False)

            chunk = AudioChunk(raw, self.audio_format)
            self.audio_stream.feed(chunk)

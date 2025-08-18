import struct
from typing import Any, AsyncGenerator
import pvporcupine
from voice.audio_stream import AudioFormat, AudioStream
from voice.wakeword import WakeWord

class PorcupineWakeWord(WakeWord):
    def __init__(self, keyword_path: str, access_key: str):
        self.porcupine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path]
        )
        #print(self.porcupine.frame_length)
        
    def detect_wakeword(self, audio_stream: AudioStream):
        """
        Retorna quando WakeWord for detectado.
        """
        buffer = None
        for audio_chunk in audio_stream.get_audio_chunks_streaming_as(AudioFormat(16000, "int16")):

            pcm = struct.unpack_from(
                    f"{self.porcupine.frame_length}h", audio_chunk.get_as("bytes")
                )
            
            #if buffer is None:
            #    buffer = audio_chunk.get_as("numpy")
            #else:
            #    
            
            result = self.porcupine.process(pcm)
            if result != -1:
                return
from typing import AsyncGenerator

class Microphone:
    """
    Classe base de um microfone.
    """
    def start(self):
        raise NotImplementedError
    
    def get_audio_frames(self) -> AsyncGenerator:
        raise NotImplementedError
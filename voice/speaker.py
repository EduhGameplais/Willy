from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"

def speak(text: str):
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    wav = tts.tts(
        text=text,
        speaker_wav="my/cloning/audio.wav",
        language="pt"
    )
    #TODO: tudo
    pass

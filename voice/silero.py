import torch
import numpy as np
import time

def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

class Silero:
    def __init__(self, repo: str = "snakers4/silero-vad", model="silero_vad"):
        start_time = time.perf_counter()
        print("Loading Silero...")
        self.model, utils = torch.hub.load(repo_or_dir=repo,
                                      model=model,
                                      force_reload=False)
        end_time = time.perf_counter()
        print(f"    Took {end_time-start_time:.2}s")



    def process_audio_chunk(self, chunk_int16: bytes): 
        audio_int16 = np.frombuffer(chunk_int16, np.int16)

        return self.model(torch.from_numpy(int2float(audio_int16)), 16000).item()


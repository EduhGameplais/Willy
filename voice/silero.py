import torch
import numpy as np
import time

start_time = time.perf_counter()
print("Loading silero...")
model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                              model='silero_vad',
                              force_reload=False)
end_time = time.perf_counter()
print(f"Silero loaded. ({end_time-start_time}s))")

(get_speech_timestamps,
 save_audio,
 read_audio,
 VADIterator,
 collect_chunks) = utils

def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1/32768
    sound = sound.squeeze()  # depends on the use case
    return sound

def process_audio_chunk(chunk_int16: bytes): 
    audio_int16 = np.frombuffer(chunk_int16, np.int16)
    
    return model(torch.from_numpy(int2float(audio_int16)), 16000).item()
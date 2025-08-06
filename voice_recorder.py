import time
import pyaudio
import numpy as np

from voice import silero

def listen(silence_limit_secs: float, silero_threshold: float, return_filtered_voice: bool = False): 
    
    audio = pyaudio.PyAudio()
    
    stream = audio.open(rate=16000, channels=1, format=pyaudio.paInt16, frames_per_buffer=1024, input=True)
    
    data = []
    
    only_voice_data = []

    num_samples = 512

    continue_recording = True

    last_voice_detected = time.perf_counter()

    i = 0
    while continue_recording:
        audio_chunk = stream.read(num_samples)

        data.append(audio_chunk)

        new_confidence = silero.process_audio_chunk(audio_chunk)
        
        if new_confidence > silero_threshold:
            last_voice_detected = time.perf_counter()
            only_voice_data.append(audio_chunk)
            
        if time.perf_counter() - last_voice_detected > silence_limit_secs:
            continue_recording = False
                
        print(new_confidence)
        print(new_confidence > silero_threshold)
    if return_filtered_voice:
        return only_voice_data
    else:
        return data
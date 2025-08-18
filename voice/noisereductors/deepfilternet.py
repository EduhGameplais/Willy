
import threading
from df import init_df, enhance
import numpy as np
import torch
from voice.audio_stream import AudioChunk, AudioFormat, AudioStream, AudioStreamNormalizer, convert_chunk_to
from pyrnnoise import RNNoise
from audio_denoiser.AudioDenoiser import AudioDenoiser
from speechbrain.inference.separation import SepformerSeparation as separator
import noisereduce as nr
from scipy.signal import resample_poly
import librosa

from voice.noise_reductor import NoiseReductor

#TODO: Está colocando mais ruído no áudio doq sem ele.
class DeepFilterNetNoiseReductor(NoiseReductor):
    """
    NoiseReductor usando o DeepFilterNet2.
    """
    def __init__(self):
        """
        NoiseReductor usando o DeepFilterNet2.
        """
        self.model, self.df_state, _ = init_df()

    def remove_noise(self, audio: AudioChunk):
        """
        Remove ruído de um AudioChunk usando DeepFilterNet.
        """
        
        enhanced_audio = enhance(self.model, self.df_state, convert_chunk_to(audio, AudioFormat(48000, "float32")).get_as("tensor"))
        
        audio_chunk_i16 = convert_chunk_to(AudioChunk(enhanced_audio.unsqueeze(0), audio_format=AudioFormat(48000, "float32")), AudioFormat(16000, "int16"))
        
        return audio_chunk_i16
            

        
                
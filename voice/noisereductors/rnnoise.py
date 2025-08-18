
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
class RNNoiseNoiseReductor(NoiseReductor):
    """
    NoiseReductor usando o RNNoise.
    """
    def __init__(self):
        """
        NoiseReductor usando o RNNoise.
        """
        
        #self.model, self.df_state, _ = init_df()
        #self.model = AudioDenoiser(device="cuda", num_iterations=20)
        #self.model = separator.from_hparams(source="speechbrain/sepformer-whamr-enhancement", savedir='pretrained_models/sepformer-whamr-enhancement4')
        self.model = RNNoise(48000)

    def remove_noise(self, audio: AudioChunk) -> AudioChunk:
        """
        Remove ruído de um AudioChunk usando RNNoise.
        """
        buffer = None
        
        audio_chunk_f32_48000 = convert_chunk_to(audio, AudioFormat(48000, "float32"))
        
        for vad_signal, reduced_noise in self.model.denoise_chunk(audio_chunk_f32_48000.get_as("numpy")):
            if buffer is None:
                buffer = reduced_noise
            else:
                buffer = np.concatenate((buffer, reduced_noise), axis=1) #Nunca sofri tanto na minha vida e o problema era axis=0

        buffer = buffer.squeeze() #Tirar dimensao louca do rnnoise
        
        audio_chunk_i16 = convert_chunk_to(AudioChunk(buffer, audio_format=AudioFormat(48000, "int16")), AudioFormat(16000, "int16"))
        
        return audio_chunk_i16
            

        
                
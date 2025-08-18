import tempfile
import wave
import numpy as np
import pyaudio
import torch
import torchaudio
from speechbrain.inference.speaker import EncoderClassifier
import io


from scipy.io import wavfile
from voice.audio_stream import AudioChunk, AudioFormat, convert_chunk_to

class VoiceIdentifier:
    def __init__(self, voice_path: str, threshold: float = 0.30, device: str = "cuda"):
        self.voice_path = voice_path
        self.threshold = threshold
        self.__classifier = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        self.__similarity = torch.nn.CosineSimilarity(dim=-1, eps=1e-6) ##Adorei isso aqui
        
        self.know_voices: list[dict] = []
        
    def embed_voice(self, audio: AudioChunk, name: str):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wf = wave.open(tmpfile, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16bits
            wf.setframerate(16000)
            wf.writeframes(convert_chunk_to(audio, AudioFormat(16000, "int16")).get_as("bytes"))
            wf.close()
            
            tmp_path = tmpfile.name  # pega caminho do arquivo
        
        #print(tmp_path)
        
        waveform, sr = torchaudio.load(tmp_path)
        
        if sr != 16000:
            waveform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=16000)(waveform)
        
        emb = self.__classifier.encode_batch(waveform).detach().cuda().squeeze(0)
        
        entry = next((e for e in self.know_voices if e["name"] == name), None)
        
        if entry:
            entry["emb"] = emb
        else:
            self.know_voices.append({"name": name, "emb": emb})
            
    def get_know_peoples(self) -> list[str]:
        return [x["name"] for x in self.know_voices]
    
    def identify_voice(self, audio: AudioChunk):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            wf = wave.open(tmpfile, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16bits
            wf.setframerate(16000)
            wf.writeframes(audio.get_as("bytes"))
            wf.close()
            
            tmp_path = tmpfile.name  # pega caminho do arquivo
        
        print(audio.get_as("numpy"))
        
        wavfile.write("output.wav", 16000, convert_chunk_to(audio, AudioFormat(16000, "int16")).get_as("numpy"))
        
        print(tmp_path)
        
        waveform, sr = torchaudio.load(tmp_path)
        
        emb = self.__classifier.encode_batch(waveform).detach().cuda().squeeze(0)
        
        for voice in self.know_voices:
            cos_sim = self.__similarity(emb, voice['emb']).item()
            
            if cos_sim > self.threshold:
                return voice["name"]
            
        return "Desconhecido"
            
            
            
            
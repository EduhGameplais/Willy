#Não completo, da erro.

import queue
import threading
import time
import wave
import numpy as np
import pyaudio
import torch
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
import sounddevice as sd
from scipy.signal import resample

device = "cuda" if torch.cuda.is_available() else "cpu"

checkpoint_path = "/run/media/edu/HD/Projects/Willy/xtts/"
config_path = f"/run/media/edu/HD/Projects/Willy/xtts/config.json"

class Speaker:
    def __init__(self, speaker_wav: str, xtts_streaming_chunk_size: int = 5):
        config = XttsConfig()
        config.load_json(config_path)
        self.model = Xtts.init_from_config(config)
        self.model.load_checkpoint(config, checkpoint_path=checkpoint_path+"model.pth", use_deepspeed=False, vocab_path=checkpoint_path+"vocab.json", checkpoint_dir=checkpoint_path)
        self.model.cuda()
        
        self.xtts_streaming_chunk_size = xtts_streaming_chunk_size
        
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(audio_path=[speaker_wav])

        
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        
        self.running = True
        self.thread_speaker = threading.Thread(target=self.__speak_audio_worker, daemon=True)
        self.thread_generator = threading.Thread(target=self.__generate_audio_worker, daemon=True)
        self.thread_speaker.start()
        self.thread_generator.start()

    def clone_voice(self, audio: list[bytes]):
        #converter de 16khz(para whisper) pra 24khz(pra XTTS)
        audio_rate = 16000
        wav_rate = 24000
        
        audio_data = b''.join(audio)
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        new_length = int(len(samples) * audio_rate / wav_rate)
        
        resampled = resample(samples, new_length).astype(np.int16)
        
        with wave.open("cloning_voice.wav", 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
            wf.setframerate(wav_rate)
            wf.writeframes(b''.join(resampled))
        self.gpt_cond_latent, self.speaker_embedding = self.model.get_conditioning_latents(
            audio_path=["cloning_voice.wav"]
        )


    def stop(self):
        sd.stop()
        self.running = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
    
    def __speak_audio_worker(self):
        # Abre o stream de saída contínuo
        with sd.OutputStream(samplerate=24000, channels=1, dtype='float32') as stream:
            while True:
                if not self.running:
                    time.sleep(0.05)
                    continue
                
                audio = self.audio_queue.get()

                # Converte o tensor para numpy float32
                audio_np = audio.cpu().numpy().astype(np.float32)

                # Envia para reprodução contínua
                stream.write(audio_np)

    def __generate_audio_worker(self):
        while True:
            if self.running == False:
                time.sleep(0.1)
                continue
            text = self.text_queue.get()
        
            chunks = self.model.inference_stream(
               text,
               "pt",
               self.gpt_cond_latent,
               self.speaker_embedding,
               stream_chunk_size=self.xtts_streaming_chunk_size
            )
            for chunk in chunks:
                self.audio_queue.put(chunk) ##Mudar para .cpu em caso de erro.

    def speak(self, text: str):
        """
        Adiciona o texto numa fila para ser reproduzido 
        """
        
        if self.running == False:
            self.audio_queue = queue.Queue()
            self.text_queue = queue.Queue()
            self.running = True
            
        self.text_queue.put(text)
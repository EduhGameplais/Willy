import time
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline, BitsAndBytesConfig
import numpy as np

from voice.audio_stream import AudioChunk

class Transcriber:
    def __init__(self, whisper_model: str, device: str = "cuda", use_8bit: bool = False):
        print("Loading Whisper...")
        start_time = time.perf_counter()
        if use_8bit:
           # 8-bit 
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_enable_fp32_cpu_offload=True
            )
            
            model = AutoModelForSpeechSeq2Seq.from_pretrained(
                whisper_model,
                quantization_config=quantization_config,
                device_map={"": torch.device("cuda:0")},  # Aqui, como eu faço para por apenas para rodar na gpu?
            )
            
            processor = AutoProcessor.from_pretrained(whisper_model)
            
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model,
                tokenizer=processor.tokenizer,
                feature_extractor=processor.feature_extractor,
            )
        else:
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=f"{whisper_model}",
                torch_dtype=torch.float16,
                device=f"{device}:0",
            )
            
            #self.pipe.model = self.pipe.model.to_bettertransformer()
        end_time = time.perf_counter()
        time_took = end_time-start_time
        print(f"    Took {time_took:.2}s")

    def transcribe(self, audio: AudioChunk):
        # The audio buffer needs to be converted to a numpy array
        audio_np = np.frombuffer(audio.get_as("bytes"), dtype=np.int16).astype(np.float32) / 32768.0

        # The pipeline expects a dictionary with the raw audio data.
        # We also specify that it should generate timestamps.
        result = self.pipe({"raw": audio_np, "sampling_rate": 16000}) #generate_kwargs={"language": "portuguese"}
        
        text = result.get("text", "")
        
        return text
import queue
import threading
from typing import Generator, Literal
import numpy as np
import torch
import torchaudio
import librosa
from scipy.signal import resample_poly
import torchaudio.functional as F


class AudioFormat:
    """
    Formato de áudio para ser usado com o AudioStream.
    Args:
        sample_rate (int): Sample rate do áudio.
        format (np.int16 or np.float32): Formato do áudio.
    """
    def __init__(self, sample_rate: int, format: Literal["int16", "float32"]):
        self.sample_rate = sample_rate
        self.format = format

class AudioChunk:
    def __init__(self, audio: bytes | torch.Tensor | np.ndarray, audio_format: AudioFormat):
        self.audio = audio
        self.audio_format = audio_format
            
    def __convert_to_bytes(self):
        if isinstance(self.audio, bytes):
            return self.audio
        elif isinstance(self.audio, np.ndarray):
            return self.audio.tobytes()
        elif isinstance(self.audio, torch.Tensor):
            return self.audio.cpu().numpy().tobytes()
        
    def __convert_to_numpy(self):
        if isinstance(self.audio, bytes):
            return np.frombuffer(self.audio, dtype=np.dtype(self.audio_format.format))
        elif isinstance(self.audio, np.ndarray):
            return self.audio
        elif isinstance(self.audio, torch.Tensor):
            return self.audio.cpu().numpy()
        
    def __convert_to_tensor(self, keep_dims: bool = True):
        if isinstance(self.audio, bytes):
            tensor = torch.from_numpy(np.frombuffer(self.audio, dtype=np.dtype(self.audio_format.format)))
        elif isinstance(self.audio, np.ndarray):
            tensor = torch.from_numpy(self.audio)
        elif isinstance(self.audio, torch.Tensor):
            tensor = self.audio

        if keep_dims and tensor.dim() == 1:
            tensor = tensor.unsqueeze(0)
        
        if not keep_dims and tensor.dim() > 1:
            tensor = tensor.squeeze(0)
        return tensor
    
    def get_as(self, type: Literal["numpy", "tensor", "bytes"], keep_dims: bool = True):
        """
        Retorna chunk de áudio no tipo.
    
        Args:
            type ("numpy", "tensor", "bytes"): Tipo de retorno do chunk.
            keep_dims (bool): Retorna tensor com .unsqueeze(0).
        """
        if type == "numpy":
            if isinstance(self.audio, np.ndarray):
                return self.audio
            return self.__convert_to_numpy()
        elif type == "tensor":
            if isinstance(self.audio, torch.Tensor):
                return self.audio
            return self.__convert_to_tensor()
        elif type == "bytes":
            if isinstance(self.audio, bytes):
                return self.audio
            return self.__convert_to_bytes()
        else:
            return self.audio
        
    def get_stored_data_type(self) -> Literal["bytes", "numpy", "tensor"]:
        if isinstance(self.audio, bytes):
            return "bytes"
        elif isinstance(self.audio, np.ndarray):
            return "numpy"
        elif isinstance(self.audio, torch.Tensor):
            return "tensor"
        return ""

class AudioStream:
    """
    Stream de áudio.
    """
    def __init__(self):
        self.chunks = queue.Queue()
        self.resamplers = []
        pass
    
    def feed(self, audio_chunk: AudioChunk):
        """
        Adiciona um chunk ao AudioStream para ser usado depois.
        """
        self.chunks.put(audio_chunk)
    
    def get_audio_chunk(self) -> AudioChunk:
        """
        Retorna um AudioChunk.
        """
        return self.chunks.get()
                
    
    def get_audio_chunk_as(self, format: AudioFormat) -> AudioChunk:
        """
        Retorna um AudioChunk convertido para o formato.
        """
        #usar o convert_chunk_to aqui.
        return convert_chunk_to(self.get_audio_chunk(), format)
    
    def get_audio_chunks_streaming(self) -> Generator:
        while True:
            yield self.get_audio_chunk()
    
    def get_audio_chunks_streaming_as(self, format: AudioFormat) -> Generator:
        while True:
            chunk = self.get_audio_chunk()
            yield convert_chunk_to(chunk, format)
                        
            
class AudioStreamNormalizer:
    """
    Normaliza o tamanho dos AudioChunks para o chunk_size definido. 
    
    Nota: Os AudioChunks no AudioStream precisam estar no mesmo formato.
    """
    def __init__(self, stream: AudioStream, output_format: AudioFormat, chunk_size: int = 512):
        self.stream = stream
        self.local_stream = AudioStream()
        self.output_format = output_format
        self.chunk_size = chunk_size
        self.__internal_buffer: bytearray = bytearray()
        threading.Thread(target=self.__consume_stream_audio_chunks, daemon=True).start()
    
    def __consume_stream_audio_chunks(self):
        for chunk in self.stream.get_audio_chunks_streaming_as(self.output_format):
            data = chunk.get_as("bytes", keep_dims=False)

            self.__internal_buffer.extend(data)

            n_samples = len(self.__internal_buffer) // np.dtype(self.output_format.format).itemsize

            while n_samples >= self.chunk_size:
                n_bytes = self.chunk_size * np.dtype(self.output_format.format).itemsize
                out = bytes(self.__internal_buffer[:n_bytes])
                self.__internal_buffer = self.__internal_buffer[n_bytes:]

                self.local_stream.feed(AudioChunk(out, self.output_format))

                n_samples = len(self.__internal_buffer) // np.dtype(self.output_format.format).itemsize
    
    def feed(self, audio_chunk: AudioChunk):
        self.stream.feed(audio_chunk)
    
    def get_audio_chunk(self) -> AudioChunk:
        return self.local_stream.get_audio_chunk()
    
    def get_audio_chunk_as(self, format: AudioFormat) -> AudioChunk:
        return self.local_stream.get_audio_chunk_as(format)
    
    def get_audio_chunks_streaming(self) -> Generator:
        return self.local_stream.get_audio_chunks_streaming()
    
    def get_audio_chunks_streaming_as(self, format: AudioFormat) -> Generator:
        return self.local_stream.get_audio_chunks_streaming_as(format)


def convert_chunk_to(chunk: AudioChunk, output_audio_format: AudioFormat):
    if chunk.audio_format == output_audio_format:
        return chunk

    audio_converted = convert_chunk_dtype(chunk.get_as("numpy"), "float32")

    # converte para tensor [1, time] porque o torchaudio espera isso
    #audio_tensor = torch.from_numpy(audio_converted).unsqueeze(0)
    
    resampled = librosa.resample(audio_converted, orig_sr=chunk.audio_format.sample_rate, target_sr=output_audio_format.sample_rate)  

    resampled = np.clip(resampled, -1, 1)
    resampled = convert_chunk_dtype(resampled, output_audio_format.format)

    return AudioChunk(resampled, output_audio_format)

def convert_chunk_dtype(chunk: np.ndarray, oformat):
    if chunk.dtype == np.int16:
        if oformat == "float32":
            return chunk.astype(np.float32) / 32768.0
        else:
            return chunk

    if chunk.dtype == np.float32:
        if oformat == "int16":
            resampled = np.clip(chunk, -1, 1)
            return (resampled * 32767.0).astype(np.int16)
        else:
            return chunk
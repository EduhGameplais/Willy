import asyncio
from enum import Enum
from typing import Callable
from voice.audio_stream import AudioFormat, AudioStreamNormalizer
from voice.microphone import Microphone
from voice.noisereductors.deepfilternet import NoiseReductor
from voice.transcriber import Transcriber
from voice.voice_identifier import VoiceIdentifier
from voice.voice_recorder import SileroVoiceRecorder
from voice.wakeword import WakeWord
from scipy.io import wavfile

class VoiceStatus(Enum):
    WaitingWakeWord = 1
    Recording = 2
    RecognizingVoice = 3
    Transcribing = 4
    Output = 5

class VoiceManager:
    """
    Manager de todo o processo de voz do Willy, desde detecção de Wake Word a Transcrição do áudio.
    """
    def __init__(self, wakeword: WakeWord, microphone: Microphone, transcriber: Transcriber, voice_identifier: VoiceIdentifier, noise_reductor: NoiseReductor):
        self.wakeword = wakeword
        self.microphone = microphone
        self.transcriber = transcriber
        self.voice_identifier = voice_identifier
        self.noise_reductor = noise_reductor
        self.last_voice_recorded = None
        
        
    def set_last_voice_name(self, name: str):
        if self.last_voice_recorded:
            self.voice_identifier.embed_voice(self.last_voice_recorded, name)
    
    def start(self, status_update_callback: Callable[[VoiceStatus, str], None]):
        stream = AudioStreamNormalizer(self.microphone.start(), output_format=AudioFormat(16000, "int16"))
        
        recorder = SileroVoiceRecorder(silence_limit_secs=1, silero_threshold=0.3)
        
        while True:
            status_update_callback(VoiceStatus.WaitingWakeWord, "")

            self.wakeword.detect_wakeword(stream)
            
            status_update_callback(VoiceStatus.Recording, "")
            
            audio, filtered_audio = recorder.listen(stream)
            
            wavfile.write("output2.wav", 16000, audio.get_as("numpy"))
            
            denoised_audio = self.noise_reductor.remove_noise(audio)
            
            wavfile.write("output3.wav", 16000, denoised_audio.get_as("numpy"))

            self.last_voice_recorded = audio
            
            status_update_callback(VoiceStatus.RecognizingVoice, "")
            
            voice_name = self.voice_identifier.identify_voice(denoised_audio)
            
            status_update_callback(VoiceStatus.Transcribing, "")
            
            transcription = self.transcriber.transcribe(denoised_audio)
            
            status_update_callback(VoiceStatus.Output, f"{voice_name}: {transcription}")
        
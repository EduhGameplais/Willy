import queue
import threading
from piper import PiperVoice, SynthesisConfig
import sounddevice as sd

class Speaker:
    """
    Classe para usar o pipertts no willy.
    
    · Carrega o piper tts e inicia os workers da fila.
    """
    def __init__(self, model_path: str = "/run/media/edu/HD/Projects/Willy/Prototipos/jeff/pt_BR-jeff-medium.onnx", use_cuda: bool = False):
        self.model = PiperVoice.load(model_path, use_cuda=use_cuda)
        
        #Inicia as filas
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        
        #Define running como True para os workers da fila funcionarem.
        self.running = True
        
        self.thread_speaker = threading.Thread(target=self.__speak_audio_worker, daemon=True)
        self.thread_generator = threading.Thread(target=self.__generate_audio_worker, daemon=True)
        
        self.thread_speaker.start()
        self.thread_generator.start()
        pass
    
    
    def __speak_audio_worker(self):
        while True:
            if self.running:
                #Pega um chunk de áudio da fila
                audio_chunk = self.audio_queue.get()
                
                #Reproduz chunk
                sd.play(audio_chunk, samplerate=22050)
                sd.wait()
    
    def __generate_audio_worker(self):
        while True:
            if self.running:
                #Pega um chunk de texto da fila
                text = self.text_queue.get()
                audio_chunks = self.model.synthesize(text)
                
                #Itera por cada chunk gerado
                for chunk in audio_chunks:
                    #e adiciona ele na fila para ser reproduzido depois
                    self.audio_queue.put(chunk.audio_int16_array)
        
    
    def stop(self):
        """Encerra a geração de voz atual, pausa a reprodução e limpa as filas de texto e audio."""
        
        #Reseta as filas
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        
        #Pausa a reprodução de audio
        sd.stop()
    
    def speak(self, text: str):
        """Adiciona texto a fila do piper tts"""
        
        #Adiciona o texto na fila
        self.text_queue.put(text)
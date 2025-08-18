import time
from voice.audio_stream import AudioFormat
from voice.microphones.local_microphone import LocalMicrophone
from voice.microphones.web_microphone import WebMicrophone
from voice.noisereductors.deepfilternet import DeepFilterNetNoiseReductor
from voice.transcriber import Transcriber
from voice.voice_identifier import VoiceIdentifier
from voice.wakewords.porcupine_wakeword import PorcupineWakeWord
from voice_manager import VoiceManager, VoiceStatus
import re
from llm.context import SystemMessage, UserMessage
from llm.llm import LLM
from voice.piper import Speaker
from tool_manager import scan_tools
tools = scan_tools()

        #model="qwen3:8b"
llm = LLM(model="qwen3:8b", tools=tools)

llm.context.add_message(SystemMessage("Fale apenas em português. Faça respostas curtas mas íntegras."))

tts = Speaker(model_path="/run/media/edu/HD/Projects/Willy/Prototipos/jeff/pt_BR-jeff-medium.onnx", use_cuda=False)

phrase_text = ""
phrase_count = 0

start_time = 0

first_token_speaked = False

def process_token(token:str):
    global phrase_text, phrase_count
    emoji_pattern = re.compile( # Magia negra do chat gtp.
        "["
        "\U0001F600-\U0001F64F" 
        "\U0001F300-\U0001F5FF" 
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002500-\U00002BEF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )

    token = emoji_pattern.sub('', token)
    
    phrase_text += token.replace('.', '').replace(':', ' ').replace(';', '').replace('*', '').replace('\n',' ')
    if '.' in token or '!' in token or '?' in token or ': ' in token:
        print(f"PHRASE{phrase_count}: {phrase_text}")
        tts.speak(phrase_text)
        global start_time, first_token_speaked
        if not first_token_speaked:
            first_token_speaked = True
            end_time = time.perf_counter()
            time_used = end_time - start_time
            print(f"Time to Voice Response: {time_used:.2}")
        phrase_text = ""
        phrase_count+=1

wakeword = PorcupineWakeWord("/run/media/edu/HD/Projects/Willy/voice/wakewords/Hey-Willy_en_linux_v3_0_0.ppn", "RTe4XZghbO2MEmfdOjh3KltYc9T/bxZn09cWsnG5PVmpKVJCrk7wPg==")
microphone = WebMicrophone() #num_frames=512, audio_format=AudioFormat(16000, "int16")
transcriber = Transcriber("openai/whisper-medium")
voice_identifier = VoiceIdentifier("")
noise_reductor = DeepFilterNetNoiseReductor()

voice = VoiceManager(wakeword, microphone, transcriber, voice_identifier, noise_reductor)

def voice_callback(status: VoiceStatus, result: str):
    global start_time
    
    print(status.name + " " + result)
    end_time = time.perf_counter()
    diff = end_time - start_time
    print(f"Used Time: {diff:.2}s")
    
    if status == VoiceStatus.Output:
        voice.set_last_voice_name("Eduardo")
    
    start_time = time.perf_counter()

voice.start(voice_callback)

 
input("Press enter to start recording.")
    
    
    #llm.context.add_message(UserMessage(transcription))

    #print("Willy: ", end='')
    #llm.get_response_stream(token_callback=process_token)
    #if not first_token_speaked:
    #    tts.speak(phrase_text)
    #    end_time = time.perf_counter()
    #    time_used = end_time - start_time
    #    print(f"Time to Voice Response: {time_used:.2}")
    #print()

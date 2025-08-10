import os
import time

face_path = os.path.abspath("face/index.html")
print(f"Opening: {face_path}")
#subprocess.Popen(["xdg-open", face_path])

import re
from llm.context import SystemMessage, UserMessage
from llm.llm import LLM
from voice.piper import Speaker
from voice_recorder import VoiceRecorder
from tool_manager import scan_tools
from voice.transcriber import Transcriber

tools = scan_tools()

recorder = VoiceRecorder(silence_limit_secs=1, silero_threshold=0.5)

transcriber = Transcriber("openai/whisper-medium", "cuda", True)

llm = LLM(tools=tools)

llm.context.add_message(SystemMessage("Speak in the Portuguese language. Write the answer in just one line without using special characters."))

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
    if '.' in token or '!' in token or '?' in token or ':' in token:
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


while True:
    input("Press enter to start recording.")
    audio, filered_audio = recorder.listen()
    first_token_speaked = False
    start_time = time.perf_counter()

    transcription = transcriber.transcribe(filered_audio)

    print(f"You said: {transcription}")

    llm.context.add_message(UserMessage(transcription))

    print("Willy: ", end='')
    llm.get_response_stream(token_callback=process_token)
    print()

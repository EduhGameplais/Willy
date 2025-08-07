#import numpy as np
#import openai
from llm.context import LLMContext, SystemMessage, UserMessage
from llm.llm import LLM
#from voice_recorder import listen
from function_manager import scan_functions
#from voice.transcriber import Transcriber

functions = scan_functions()
#transcriber = Transcriber("medium") 

#audio = listen(3, 0.5, True)

llm = LLM(tools=functions)

llm.context.add_message(SystemMessage("Fale na lingua que o usuário fala."))

llm.context.add_message(UserMessage("what time is in washington"))

def process_token(token:str):
    print(token, end='')

llm.get_response_stream(process_token)

#print(transcriber.transcribe(audio))
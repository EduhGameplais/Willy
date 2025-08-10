from typing import Callable
from llm.context import AssistantMessage, LLMContext, ToolMessage
from ollama import chat

#TODO: Usar OLLAMA.

class LLM:
    def __init__(self, model: str = "PetrosStav/gemma3-tools:4b", tools: list[Callable] = [], ollama_url = ""):
        self.model = model
        self.context = LLMContext()
        self.ollama_url = ollama_url
        self.tools = tools
        
    def get_response_stream(self, token_callback: Callable[[str], None]):
        stream_resp = chat(
            model=self.model,
            messages=self.context.get_messages_for_ollama(),
            tools=self.tools,
            stream=True
        )

        full_msg = ""
        
        have_tool_call = False
        
        for chunk in stream_resp:
            msg = chunk.message
            if msg.content:
                token_callback(msg.content)
                full_msg += msg.content
            if msg.tool_calls:
                have_tool_call = True
                if full_msg != "":
                    self.context.add_message(AssistantMessage(content=full_msg))
                self.context.add_message(AssistantMessage(tool_calls=msg.tool_calls))
                for tool_call in msg.tool_calls:
                    tool_name = tool_call["function"]["name"]
                    
                    tool_executor = next(
                        (f for f in self.tools if f.__name__ == tool_name),
                        None
                    )
                    
                    if tool_executor:
                        args = tool_call["function"]["arguments"]
                        result = tool_executor(**args)
                        self.context.add_message(ToolMessage(tool_name=tool_name, content=result))

                self.get_response_stream(token_callback)
        
        if not have_tool_call:
            if full_msg != "":
                    self.context.add_message(AssistantMessage(content=full_msg))


class UserMessage:
    def __init__(self, content: str, images: list[str] = None):
        self.content = content
        self.images = images

class AssistantMessage:
    def __init__(self, content: str = None, tool_calls: list = None):
        self.tool_calls = tool_calls     
        self.content = content
        
        if tool_calls == None and content == None:
            raise ValueError("It is not possible to create an assistant message without 'tool_calls' or 'content'.")

class ToolMessage:
    def __init__(self, tool_name: str, content: str):
        self.content = content
        self.tool_name = tool_name

class SystemMessage:
    def __init__(self, content: str):
        self.content = content
        
class LLMContext:
    def __init__(self):
        self.messages = []
        self.system_prompt = ""
        pass
    
    def add_message(self, message: SystemMessage | UserMessage | AssistantMessage | ToolMessage):
        self.messages.append(message)
        pass
    
    def get_messages_for_ollama(self):
        context = []
        
        if self.system_prompt != "":
            context.append({
                "role": "system",
                "content": self.system_prompt,
            })
        
        for message in self.messages:
            
            if isinstance(message, SystemMessage):
                context.append({
                    "role": "system",
                    "content": message.content,
                })
                
            elif isinstance(message, UserMessage):
                item = {
                    "role": "user",
                    "content": message.content,
                }
                if message.images is not None:
                    item["images"] = message.images
                context.append(item)
                
            elif isinstance(message, AssistantMessage):
                item = {
                    "role": "assistant",
                }
                if message.content is not None:
                    item["content"] = message.content
                if message.tool_calls is not None:
                    item["tool_calls"] = message.tool_calls
                context.append(item)
                
            elif isinstance(message, ToolMessage):
                context.append({
                    "role": "tool",
                    "name": message.tool_name,
                    "content": message.content,
                })
        
        return context
    
    def get_messages_for_gemini(self):
        context = []
        
        if self.system_prompt != "":
            pass
        
        for message in self.messages:
            if isinstance(message, SystemMessage):
                
                pass
                
            elif isinstance(message, UserMessage):
                content = message.content
                if self.system_prompt != "":
                    content = self.system_prompt + "\n\n" + content
                    self.system_prompt = ""
                item = {
                    "role": "user",
                    "parts": [content],
                }
                context.append(item)
                
            elif isinstance(message, AssistantMessage):
                item = {
                    "role": "model",
                    "parts": [],
                }
                if message.content is not None:
                    item["parts"].append(message.content)
                if message.tool_calls is not None:
                    tool_calls = []
                    for tool_call in message.tool_calls:
                        tool_calls.append({
                            "function_call": {
                                "name": tool_call["function"]["name"],
                                "args": tool_call["function"]["arguments"],
                            }
                        })
                    item["parts"].extend(tool_calls)
                context.append(item)
                
            elif isinstance(message, ToolMessage):
                context.append({
                    "role": "tool",
                    "parts": [{
                        "function_response": {
                            "name": message.tool_name,
                            "response": {
                                "content": message.content
                            }
                        }
                    }]
                })
        
        return context
    
    def get_context_for_local(self):
        return self.messages
        pass
    
    def set_system_prompt(self, prompt):
        self.system_prompt = prompt

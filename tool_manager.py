import importlib
import os


def scan_tools():
    """Faz scan de tools para LLM na pasta 'tools'."""

    tools = []
    
    tools_available = "Tools Available: "
    
    with os.scandir("tools") as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".py"):
                function_name = entry.name[:-3]
                function = importlib.import_module(f"tools.{function_name}")
                
                if hasattr(function, function_name):
                    tools_available += function_name + ", "
                    func = getattr(function, function_name)
                    tools.append(func)
    print(tools_available)
    return tools
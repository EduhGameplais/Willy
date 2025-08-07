import importlib
import os

def scan_functions():
    functions = []
    
    with os.scandir("functions") as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".py"):
                function_name = entry.name[:-3]
                
                function = importlib.import_module(f"functions.{function_name}")
                
                if hasattr(function, function_name):
                    print(f"Loaded function '{function_name}'.")
                    func = getattr(function, function_name)
                    functions.append(func)
                    
    return functions
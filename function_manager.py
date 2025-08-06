import importlib
import os

def scan_functions():
    with os.scandir("functions") as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".py"):
                function_name = entry.name[:-3]
                
                function = importlib.import_module(f"functions.{function_name}")
                
                if hasattr(function, "run"):
                    print(f"{function_name} is an valid function")
                    function.run()
                    
                
                print(entry.name)
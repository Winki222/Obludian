import json
from pathlib import Path
import platform
config_path = Path(__file__).parent.parent / "config.json"
def load_config():
    try:
        with open(config_path,"r", encoding='utf-8') as file:
            data=json.load(file)
            if data["vault_path"] is None:
                print("Предупреждение: vault_path не указан в config.json")
        return data
                
    except Exception as e:
        print(e)

def detect_platform():
    system=platform.system()
    if system=="Linux":
        if Path("/data/data/com.termux").exists():
            return "Termux"
    return system
import json


class ConfigLoader:

    @staticmethod
    def load(path: str):
        with open(path) as f:
            config = json.load(f)
            return config
    
    @staticmethod
    def save(path: str, json_content: dict):
        with open(path, 'w+', encoding='utf-8') as outfile:
            json.dump(json_content, outfile, ensure_ascii=False, indent='\t')

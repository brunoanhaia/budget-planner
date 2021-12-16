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

    @staticmethod
    def update(path: str, update_dict: dict):
        config_content = ConfigLoader.load(path)

        update_type = update_dict.get('type', None)

        if (update_type == "user"):
            cpf = update_dict.get('key')
            update_values: dict = update_dict.get('update_values')

            for user in config_content['users']:
                if user['cpf'] == cpf:
                    for update_value_key in update_values:
                        user[update_value_key] = \
                            update_values[update_value_key]

        ConfigLoader.save(path, config_content)

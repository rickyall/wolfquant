import json


def config(filepath):
    """配置文件
    """
    with open(filepath, encoding='utf8') as json_file:
        return json.load(json_file)
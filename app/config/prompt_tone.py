import json
from pathlib import Path


class PromptTone:
    prompt: str
    rules: list[str]


def read_json_file(file_path: Path) -> PromptTone:
    with file_path.open("r") as file:
        data = json.load(file)
    return data


directory = Path("./config")
file_name = "prompt_tone.json"

file_path = directory / file_name

prompt_tone_conf = read_json_file(file_path)
prompt_tone = f"{prompt_tone_conf["prompt"]}\n {"\n".join(prompt_tone_conf["rules"])}"

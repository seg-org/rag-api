import json
import os
from pathlib import Path
from typing import Dict, TypedDict


class PromptTone:
    prompt: str
    rules: list[str]


def read_json_file(file_path: Path) -> PromptTone:
    with file_path.open("r") as file:
        data = json.load(file)
    return data


directory = Path(".")
file_name = "prompt_tone.json"

file_path = directory / file_name

prompt_tone = read_json_file(file_path)

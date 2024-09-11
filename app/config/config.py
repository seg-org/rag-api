import os

from dotenv import load_dotenv

from .prompt_tone import prompt_tone

load_dotenv()


class AppConfig:
    env = os.getenv("APP_ENV")
    port = int(os.getenv("APP_PORT"))


class DbConfig:
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")


class Config:
    app = AppConfig()
    db = DbConfig()
    enable_prompt_tone = os.getenv("ENABLE_PROMPT_TONE")
    prompt_tone = prompt_tone


config = Config()

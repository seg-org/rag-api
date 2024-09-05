import os

from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    env = os.getenv("APP_ENV")
    port = int(os.getenv("APP_PORT"))


class LangchainConfig:
    api_key = os.getenv("LANGCHAIN_API_KEY")
    is_tracing = os.getenv("LANGCHAIN_TRACING_V2")


class DbConfig:
    url = os.getenv("DB_URL")


class Config:
    app = AppConfig()
    langchain = LangchainConfig()
    db = DbConfig()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embedding_api_host = os.getenv("EMBEDDING_API_HOST")


config = Config()

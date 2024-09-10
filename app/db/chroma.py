import logging

import chromadb
from chromadb.config import Settings
from config import config
from main import llm


class DB:
    def __init__(self):
        settings = Settings(
            chroma_server_host=config.db.host,
            chroma_server_http_port=config.db.port,
        )
        client = chromadb.Client(settings=settings)
        self.collection = client.create_collection("my_collection")

    def add_text(self, text: str):
        try:
            self.collection.add(embeddings=llm.embed(text), ids=1)
        except Exception as e:
            logging.error(f"Error completing chat: {e}")
            return ""

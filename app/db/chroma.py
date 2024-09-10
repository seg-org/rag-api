import logging
from typing import List

import chromadb
from chromadb.config import Settings
from config import config
from langchain_openai import OpenAIEmbeddings


class DB:
    __embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

    def __init__(self):
        settings = Settings(
            chroma_server_host=config.db.host,
            chroma_server_http_port=config.db.port,
        )
        client = chromadb.Client(settings=settings)
        self.collection = client.create_collection("my_collection")

    def add_text(self, text: str):
        try:
            self.collection.add(embeddings=self.embed(text), ids="1")
            logging.info("Text added to database")
        except Exception as e:
            logging.error(f"Error completing chat: {e}")
            return ""

    def embed(self, text: str) -> List[float]:
        try:
            return self.__embedding_model.embed_query(text)
        except Exception as e:
            logging.error(f"Error embedding text: {e}")
            return []

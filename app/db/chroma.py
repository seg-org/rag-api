from logging import Logger

from chromadb.config import Settings
from config import config
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DB:
    def __init__(self, log: Logger):
        self.log = log
        settings = Settings(
            chroma_api_impl="chromadb.api.fastapi.FastAPI",
            chroma_server_host=config.db.host,
            chroma_server_http_port=config.db.port,
        )
        self.vectorstore = Chroma(
            collection_name="test",
            client_settings=settings,
            embedding_function=NomicEmbeddings(
                model="nomic-embed-text-v1.5", inference_mode="local"
            ),
        )
        self.retriever = self.vectorstore.as_retriever()

    def add_web(self, url: str):
        try:
            docs_list = WebBaseLoader(url).load()
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=250, chunk_overlap=0
            )
            doc_splits = text_splitter.split_documents(docs_list)

            self.vectorstore.add_documents(documents=doc_splits)
            self.log.info("Web document added to database:", url)
            return "Web document added successfully: " + url
        except Exception as e:
            self.log.error(f"Error adding web document: {e}")
            return ""

    def add_text(self, text: str):
        try:
            self.vectorstore.add_texts(texts=[text])
            self.log.info("Text added to database:", text)
            return "Text added successfully: " + text
        except Exception as e:
            self.log.error(f"Error adding text: {e}")
            return ""

    def get_all(self):
        try:
            results = self.vectorstore.get()
            return results
        except Exception as e:
            self.log.error(f"Error getting all texts: {e}")
            return ""

    def get_relevant_text(self, text: str):
        try:
            results = self.retriever.invoke(text)
            return [r.page_content for r in results]
        except Exception as e:
            self.log.error(f"Error getting relevant text: {e}")

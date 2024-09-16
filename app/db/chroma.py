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
        self.docs_store = Chroma(
            collection_name="docs",
            client_settings=settings,
            embedding_function=NomicEmbeddings(
                model="nomic-embed-text-v1.5", inference_mode="local"
            ),
        )

    def add_web(self, url: str, guild_id: str):
        try:
            docs_list = WebBaseLoader(url).load()
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=250, chunk_overlap=0
            )
            guilded_docs = []
            for d in docs_list:
                d.metadata["guild_id"] = guild_id
                guilded_docs.append(d)

            doc_splits = text_splitter.split_documents(guilded_docs)

            self.docs_store.add_documents(documents=doc_splits)

            return "Web document added successfully: " + url
        except Exception as e:
            self.log.error(f"Error adding web document: {e}")
            return e.__str__()

    def add_text(self, text: str, guild_id: str):
        try:
            self.docs_store.add_texts(texts=[text], metadatas=[{"guild_id": guild_id}])
            return "Text added successfully: " + text
        except Exception as e:
            self.log.error(f"Error adding text: {e}")
            return e.__str__()

    def get_docs_retriever(self, guild_id: str):
        return self.docs_store.as_retriever(
            search_kwargs={"k": 20, "filter": {"guild_id": guild_id}}
        )

    def get_all_docs(self, guild_id: str):
        try:
            results = self.docs_store.get(where={"guild_id": guild_id})
            return results
        except Exception as e:
            self.log.error(f"Error getting all texts: {e}")
            return e.__str__()

    def add_borrow_money(
        self, borrower: str, lender: str, amount: float, guild_id: str
    ):
        try:
            text = f"{borrower.title()} owes {lender.title()} {amount}"

            self.docs_store.add_texts(texts=[text], metadatas=[{"guild_id": guild_id}])
            return "Debt added successfully: " + text
        except Exception as e:
            self.log.error(f"Error adding text: {e}")
            return e.__str__()

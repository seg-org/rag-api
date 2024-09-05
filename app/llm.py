from typing import List

from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


class LLM:
    __embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    __chat_completion_model = ChatOpenAI(model="gpt-3.5-turbo")
    __store = {}
    __config = {"configurable": {"session_id": "main"}}

    def __init__(self):
        self.__with_message_history = RunnableWithMessageHistory(
            self.__chat_completion_model, self.__get_session_history
        )

    def __get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.__store:
            self.__store[session_id] = InMemoryChatMessageHistory()
        return self.__store[session_id]

    def embed(self, text: str) -> List[float]:
        return self.__embedding_model.embed_query(text)

    def complete_chat(self, content: str) -> str:
        response = self.__with_message_history.invoke(
            [HumanMessage(content=content)],
            config=self.__config,
        )

        return response.content

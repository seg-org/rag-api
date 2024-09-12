from logging import Logger

from config import config
from db import DB
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


class LLM:
    __config = {"configurable": {"thread_id": "main"}}
    __tone_model = ChatOpenAI(model="gpt-3.5-turbo")

    def __init__(self, db: DB, log: Logger):
        self.db = db
        self.log = log
        self.guild_memory_store: dict[str, MemorySaver] = {}
        self.chat_completion_model = ChatOpenAI(model="gpt-3.5-turbo")

    def get_memory_for_guild(self, guild_id):
        if guild_id not in self.guild_memory_store:
            self.guild_memory_store[guild_id] = MemorySaver()
        return self.guild_memory_store[guild_id]

    def complete_chat(self, query: str, guild_id: str) -> str:
        try:
            ######################################
            docs_tool = create_retriever_tool(
                self.db.get_docs_retriever(guild_id),
                "docs_retriever",
                "Searches documents in the database that are relevant to query input.",
            )

            chat_tool = create_retriever_tool(
                self.db.get_chat_retriever(guild_id),
                "chat_retriever",
                "Searches chat messages in the Discord server that are relevant to query input.",
            )
            ######################################

            web_search_tool = TavilySearchResults(
                name="web_search_tool",
                description="Search information from the internet",
            )

            tools = [
                docs_tool,
                chat_tool,
            ]

            self.agent_executor = create_react_agent(
                self.chat_completion_model,
                tools,
                checkpointer=self.get_memory_for_guild(guild_id),
            )

            responses = self.agent_executor.stream(
                {"messages": [HumanMessage(content=query)]}, config=self.__config
            )
            last_message: AIMessage
            for s in responses:
                if "agent" in s:
                    print(s["agent"]["messages"])
                    last_message = s["agent"]["messages"][0]
                elif "tools" in s:
                    print(s["tools"]["messages"])
                print("----")

            original_reply: str = last_message.content

            if not config.enable_prompt_tone:
                return original_reply

            toned_reply = self.__tone_model.invoke(
                [
                    AIMessage(content=config.prompt_tone),
                    HumanMessage(content=original_reply),
                ]
            )
            return toned_reply.content

        except Exception as e:
            self.log.error(f"Error completing chat: {e}")
            return ""

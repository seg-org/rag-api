from logging import Logger

from config import config
from db import DB
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import WikipediaQueryRun, WolframAlphaQueryRun
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
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
        self.enable_web_search: dict[str, bool] = {}
        self.chat_completion_model = ChatOpenAI(model="gpt-3.5-turbo")

    def toggle_web_search(self, guild_id: str):
        if guild_id not in self.enable_web_search:
            self.enable_web_search[guild_id] = True

        self.enable_web_search[guild_id] = not self.enable_web_search[guild_id]
        return f"Web search toggled to {self.enable_web_search[guild_id]}"

    def get_enable_web_search(self, guild_id: str):
        if guild_id not in self.enable_web_search:
            self.enable_web_search[guild_id] = True
        return self.enable_web_search[guild_id]

    def get_memory_for_guild(self, guild_id):
        if guild_id not in self.guild_memory_store:
            self.guild_memory_store[guild_id] = MemorySaver()
        return self.guild_memory_store[guild_id]

    def complete_chat(self, query: str, guild_id: str) -> str:
        try:
            docs_tool = create_retriever_tool(
                self.db.get_docs_retriever(guild_id),
                "docs_retriever",
                "Searches documents in the database that are relevant to query input.",
            )

        web_search_tool = TavilySearchResults(
            name="web_search_tool", description="Search information from the internet"
        )

        wolfram_alpha_tool = WolframAlphaQueryRun(
            api_wrapper=WolframAlphaAPIWrapper()
        )

        tools = [web_docs_tool, web_search_tool, wolfram_alpha_tool]
        
        self.agent_executor = create_react_agent(
            chat_completion_model, tools, checkpointer=memory
        )

    def complete_chat(self, query: str) -> str:
        try:
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

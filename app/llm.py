from logging import Logger

from config import config
from langchain.agents import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from main import db


class LLM:
    __config = {"configurable": {"thread_id": "main"}}
    __tone_model = ChatOpenAI(model="gpt-3.5-turbo")

    def __init__(self, log: Logger):
        self.log = log
        self.memory = MemorySaver()
        self.chat_completion_model = ChatOpenAI(model="gpt-3.5-turbo")

    def complete_chat(self, query: str, guild_id: str) -> str:
        try:
            docs_tool = Tool(
                name="docs_tool",
                func=lambda text: db.query_docs(text, guild_id),
                description="Searches documents in the database that are relevant to query input.",
            )

            chat_tool = Tool(
                name="docs_tool",
                func=lambda text: db.query_chat(text, guild_id),
                description="Searches chat messages in the Discord server that are relevant to query input.",
            )

            web_search_tool = TavilySearchResults(
                name="web_search_tool",
                description="Search information from the internet",
            )

            tools = [docs_tool, chat_tool, web_search_tool]
            self.agent_executor = create_react_agent(
                self.chat_completion_model, tools, checkpointer=self.memory
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

import logging

from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent


class LLM:
    __config = {"configurable": {"thread_id": "main"}}

    def __init__(self, retriever: BaseRetriever):
        memory = MemorySaver()
        chat_completion_model = ChatOpenAI(model="gpt-3.5-turbo")

        web_docs_tool = create_retriever_tool(
            retriever,
            "web_docs_retriever",
            "Searches and returns excerpts from the database. Mostly web-based content",
        )

        web_search_tool = TavilySearchResults(
            name="web_search_tool", description="Search information from the internet"
        )

        tools = [web_docs_tool, web_search_tool]
        self.agent_executor = create_react_agent(
            chat_completion_model, tools, checkpointer=memory
        )

    def complete_chat(self, query: str) -> str:
        try:
            queries = [query]
            responses = self.agent_executor.stream(
                {"messages": [HumanMessage(content=queries)]}, config=self.__config
            )
            last_message: AIMessage
            for s in responses:
                if "agent" in s:
                    print(s["agent"]["messages"])
                    last_message = s["agent"]["messages"][0]
                elif "tools" in s:
                    print(s["tools"]["messages"])
                print("----")

            return last_message.content

        except Exception as e:
            logging.error(f"Error completing chat: {e}")
            return ""

from logging import Logger

from config import config
from db import DB
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_community.tools import WolframAlphaQueryRun
from langchain_community.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain.chains.llm_math.base import LLMMathChain
from langchain_community.tools.google_finance.tool import GoogleFinanceQueryRun
from langchain_community.tools.google_jobs.tool import GoogleJobsQueryRun
from langchain_community.tools.google_lens.tool import GoogleLensQueryRun
from langchain_community.tools.google_scholar.tool import GoogleScholarQueryRun
from langchain_community.tools.google_trends import GoogleTrendsQueryRun
from langchain_community.tools.google_serper import GoogleSerperResults
from langchain_core.tools import Tool


from langchain_community.utilities.google_finance import GoogleFinanceAPIWrapper
from langchain_community.utilities.google_jobs import GoogleJobsAPIWrapper
from langchain_community.utilities.google_lens import GoogleLensAPIWrapper
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain_community.utilities.google_trends import GoogleTrendsAPIWrapper


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
                name="web_search_tool",
                description="Search information from the internet",
            )

            # wolfram_alpha_tool = WolframAlphaQueryRun(
            #     api_wrapper=WolframAlphaAPIWrapper()
            # )

            # yahoo_finance_tool = YahooFinanceNewsTool()

            # google_jobs_tool = GoogleJobsQueryRun(api_wrapper=GoogleJobsAPIWrapper())
            # google_trends_tool = GoogleTrendsQueryRun(api_wrapper=GoogleTrendsAPIWrapper())
            # google_lens_tool = GoogleLensQueryRun(api_wrapper=GoogleLensAPIWrapper())
            # google_serper_tool = GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper())
            # google_finance_tool = GoogleFinanceQueryRun(api_wrapper=GoogleFinanceAPIWrapper())
            # google_scholar_tool = GoogleScholarQueryRun(api_wrapper=GoogleScholarAPIWrapper())

            # calculator_tool = Tool(
            #     name="Calculator",
            #     description="Useful for when you need to answer questions about math.",
            #     func=LLMMathChain.from_llm(llm=self.chat_completion_model).run,
            #     coroutine=LLMMathChain.from_llm(llm=self.chat_completion_model).arun,
            # )

            tools = [docs_tool]
            self.log.info(f"Web search enabled: {self.get_enable_web_search(guild_id)}")
            if self.get_enable_web_search(guild_id):
                tools.append(web_search_tool)
            
            # Maybe add some condition for adding Wolfram 
            # if self.get_something(wolfram_appid):
            # tools.append(wolfram_alpha_tool)
            # tools.append(yahoo_finance_tool)
            # tools.append(calculator_tool)

            # tools += [google_jobs_tool, google_lens_tool, google_serper_tool, google_trends_tool, google_finance_tool, google_scholar_tool]


            agent_executor = create_react_agent(
                self.chat_completion_model,
                tools,
                checkpointer=self.get_memory_for_guild(guild_id),
            )

            responses = agent_executor.stream(
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

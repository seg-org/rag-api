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
    __debt_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

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

    def complete_chat(self, query: str, guild_id: str, useDebtSum: bool = False) -> str:
        try:
            if useDebtSum:
                person = query.title()
                query = f"""
                            List all transactions with "owes".
                            List all of them, don't limit the number of transactions.
                            Don't include any currency symbols, only numbers.
                            Format it as "number|borrower|owes|lender|amount".
                        """

            docs_tool = create_retriever_tool(
                self.db.get_docs_retriever(guild_id),
                "docs_retriever",
                "Searches documents in the database that are relevant to query input.",
            )

            web_search_tool = TavilySearchResults(
                name="web_search_tool",
                description="Search information from the internet",
            )

            tools = [docs_tool]
            self.log.info(f"Web search enabled: {self.get_enable_web_search(guild_id)}")
            if self.get_enable_web_search(guild_id):
                tools.append(web_search_tool)

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

            self.log.info(f"Original reply: {original_reply}")

            if useDebtSum and original_reply.strip() != "NO TRANSACTIONS FOUND":
                transactions = [t.strip() for t in original_reply.split("\n")]
                d = {}
                for t in transactions:
                    try:
                        number, borrower, owes, lender, amount = t.split("|")
                    except Exception as e:
                        self.log.error(f"Error splitting transaction: {e}")
                        self.log.info(f"Transaction: {t}")
                        continue
                    if (
                        borrower.title() != person.title()
                        and lender.title() != person.title()
                    ):
                        continue
                    other = ""
                    if borrower.title() == person.title():
                        amount = -float(amount)
                        other = lender.title()
                    else:
                        amount = float(amount)
                        other = borrower.title()

                    person = person.title()
                    if other not in d:
                        d[other] = 0

                    d[other] += amount

                borrowed_list = []
                lent_list = []

                for key, value in d.items():
                    if value == 0:
                        continue
                    elif value < 0:
                        borrowed_list.append(f"- {key}: {-value}")
                    else:
                        lent_list.append(f"- {key}: {value}")

                original_reply = f"\n{person}'s Debt Summary\n\nBorrowed:\n{'\n'.join(borrowed_list)}\n\nLent:\n{'\n'.join(lent_list)}"

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

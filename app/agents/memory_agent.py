from agno.agent import Agent
from agno.memory.v2.memory import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.models.groq import Groq
import os

class MemoryAgent:
    def __init__(self):
        self.memory = Memory(
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            db=SqliteMemoryDb(table_name="user_memories", db_file="tmp/agent.db"),
            delete_memories=False,
            clear_memories=False
        )
        self.agent = Agent(
            name="MemoryAgent",
            role="Handle queries using chat history",
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            memory=self.memory,
            enable_agentic_memory=True,
            instructions=[
                "Use chat history to answer queries.",
                "Indicate in the response that you are the MemoryAgent.",
                "Return 'No relevant history found' if no relevant memory exists."
            ],
            markdown=True,
            add_datetime_to_instructions=True,
            add_history_to_messages=True,
            num_history_runs=3
        )
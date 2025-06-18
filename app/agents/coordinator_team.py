from agno.team.team import Team
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
from agents.memory_agent import MemoryAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.rag_agent import RAGAgent
import os
import re
import asyncio
import json
import sys
from groq import Groq as GroqClient
from utils.db import get_chat_history

class MCPClient:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def send(self, method, params):
        request = json.dumps({"method": method, "params": params})
        sys.stdout.write(request + "\n")
        sys.stdout.flush()
        response_json = await self.loop.run_in_executor(None, sys.stdin.readline)
        response = json.loads(response_json.strip())
        return response.get("response", response.get("error", "Error"))

class ReasoningStockTeam:
    def __init__(self):
        self.memory_agent = MemoryAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.rag_agent = RAGAgent()
        self.groq_client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))
        self.mcp_client = None
        self.team = Team(
            name="Stock Market Team",
            mode="coordinate",
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            members=[self.memory_agent.agent, self.knowledge_agent.agent, self.rag_agent.agent],
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Collaborate to provide accurate answers about stock market data.",
                "MemoryAgent: Respond to queries about previous interactions.",
                "KnowledgeAgent: Handle CSV-based stock queries.",
                "GeneralAgent: Handle stock market queries via MCP client.",
                "Infer stock symbols from chat history for ambiguous queries.",
                "Append the responding agent's name."
            ],
            markdown=True,
            show_members_responses=True,
            enable_agentic_context=True,
            add_datetime_to_instructions=True,
            success_criteria="Accurate response with correct agent."
        )

    async def initialize_mcp_client(self):
        if self.mcp_client is None:
            self.mcp_client = MCPClient()
            print("Connected to MCP server", file=sys.stderr)
        return self.mcp_client

    def infer_context(self, query, chat_history):
        query_lower = query.lower()
        if 'price' in query_lower or 'predict' in query_lower or 'historical' in query_lower:
            symbol_map = {
                'nvidia': 'NVDA', 'amazon': 'AMZN', 'tesla': 'TSLA', 'apple': 'AAPL',
                'microsoft': 'MSFT', 'google': 'GOOGL', 'intel': 'INTC'
            }
            for entry in reversed(chat_history):
                query_text = entry['user_query'].lower()
                for company, symbol in symbol_map.items():
                    if company in query_text:
                        return {'type': 'stock', 'value': symbol}
                symbol_match = re.search(r'\b([A-Z]{1,5})\b', query_text)
                if symbol_match:
                    return {'type': 'stock', 'value': symbol_match.group(1).upper()}
        return None

    async def process_query(self, query, uploaded_file):
        memory_keywords = ['earlier', 'previous', 'history']
        if any(keyword in query.lower() for keyword in memory_keywords):
            memory_response = self.memory_agent.agent.run(query).content
            if "No relevant history found" not in memory_response:
                return f"{memory_response}\n\n*Response by MemoryAgent*", "MemoryAgent"

        knowledge_response = self.knowledge_agent.query_knowledge(query)
        if knowledge_response:
            return knowledge_response, "KnowledgeAgent"

        if uploaded_file:
            rag_response = self.rag_agent.query_rag(query, uploaded_file)
            if "Failed to process PDF" not in rag_response:
                return rag_response, "RAGAgent"

        try:
            chat_history = get_chat_history()
            history_text = "\n".join([f"User: {h['user_query']} | Agent: {h['agent_name']} | Response: {h['response']}" for h in chat_history])
            context = self.infer_context(query, chat_history)
            query_lower = query.lower()

            mcp_client = await self.initialize_mcp_client()

            general_response = None
            if context and context['type'] == 'stock':
                symbol = context['value']
                if 'price' in query_lower:
                    date_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', query)
                    params = {"symbol": symbol}
                    if date_match:
                        params["date"] = date_match.group(1)
                    response = await mcp_client.send("fetch_stock_price", params)
                    general_response = response
                elif 'historical' in query_lower:
                    response = await mcp_client.send("fetch_historical_data", {"market": symbol, "period": "1mo"})
                    general_response = "\n".join([f"{d['Date']}: Open=${d['Open']:.2f}, Close=${d['Close']:.2f}" for d in response]) if isinstance(response, list) else response
                elif 'predict' in query_lower:
                    days_match = re.search(r'(\d+)\s*(day|days)', query)
                    days_ahead = int(days_match.group(1)) if days_match else 1
                    response = await mcp_client.send("predict_stock_price", {"market": symbol, "days_ahead": days_ahead})
                    general_response = response
            if not general_response:
                general_response = await self.fallback_groq_query(query, history_text)

        except Exception as e:
            general_response = f"Error: {str(e)}"
        return f"{general_response}\n\n*Response by GeneralAgent*", "GeneralAgent"

    async def fallback_groq_query(self, query, history_text):
        system_prompt = (
            "Answer general questions using chat history for context. "
            "Defer stock market queries to specialized tools.\n\nChat History:\n{history_text}"
        )
        response = self.groq_client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[
                {"role": "system", "content": system_prompt.format(history_text=history_text)},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
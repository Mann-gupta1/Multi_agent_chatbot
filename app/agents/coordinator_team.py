from agno.team.team import Team
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
from agents.memory_agent import MemoryAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.rag_agent import RAGAgent
import os
import re
from groq import Groq as GroqClient
from utils.db import get_chat_history

class ReasoningStockTeam:
    def __init__(self):
        self.memory_agent = MemoryAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.rag_agent = RAGAgent()
        # Initialize Groq client for general queries
        self.groq_client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))
        self.team = Team(
            name="Stock Market Team",
            mode="coordinate",
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            members=[self.memory_agent.agent, self.knowledge_agent.agent, self.rag_agent.agent],
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Collaborate to provide accurate answers about stock market data, PDF content, or general questions.",
                "Use tables to display data when applicable.",
                "Indicate which agent is responding in the final output.",
                "MemoryAgent should only respond to queries explicitly asking about previous interactions (e.g., containing 'earlier', 'previous', or 'history').",
                "KnowledgeAgent should handle stock-market-specific queries (e.g., market prices, company financials).",
                "GeneralAgent should handle general knowledge queries (e.g., CEOs, capitals, presidents, news) using chat history for context.",
                "For ambiguous queries (e.g., 'who is the ceo', 'who is the president'), infer the company or country from recent chat history.",
                "Always append the responding agent's name to the response."
            ],
            markdown=True,
            show_members_responses=True,
            enable_agentic_context=True,
            add_datetime_to_instructions=True,
            success_criteria="The team provides a complete and accurate response, indicating the responding agent."
        )

    def infer_context(self, query, chat_history):
        """Infer company or country from chat history for ambiguous queries."""
        query_lower = query.lower()
        if 'ceo' in query_lower:
            # Look for company names in recent queries
            for entry in reversed(chat_history):
                query_text = entry['user_query'].lower()
                # Common company names or keywords
                company_match = re.search(r'\b(nvidia|amazon|microsoft|apple|tesla|google|intel|starbucks|[\w\s]+)\b', query_text)
                if company_match:
                    company = company_match.group(1).strip().capitalize()
                    return {'type': 'company', 'value': company}
        elif 'president' in query_lower or 'capital' in query_lower:
            # Look for country names in recent queries
            for entry in reversed(chat_history):
                query_text = entry['user_query'].lower()
                # Common country names or keywords
                country_match = re.search(r'\b(india|france|united states|china|japan|germany|[\w\s]+)\b', query_text)
                if country_match:
                    country = country_match.group(1).strip().capitalize()
                    return {'type': 'country', 'value': country}
        return None

    def process_query(self, query, uploaded_file):
        # Check memory agent for explicit memory-related queries
        memory_keywords = ['earlier', 'previous', 'history']
        if any(keyword in query.lower() for keyword in memory_keywords):
            memory_response = self.memory_agent.agent.run(query).content
            if "No relevant history found" not in memory_response:
                return f"{memory_response}\n\n*Response by MemoryAgent*", "MemoryAgent"

        # Check knowledge agent for stock-market-specific queries
        knowledge_response = self.knowledge_agent.query_knowledge(query)
        if knowledge_response:
            return knowledge_response, "KnowledgeAgent"

        # Check RAG agent if PDF is uploaded
        if uploaded_file:
            rag_response = self.rag_agent.query_rag(query, uploaded_file)
            if "Failed to process PDF" not in rag_response:
                return rag_response, "RAGAgent"

        # Handle general knowledge queries (e.g., CEOs, capitals, presidents, news) with chat history context
        try:
            # Retrieve chat history for context
            chat_history = get_chat_history()
            history_text = "\n".join([f"User: {h['user_query']} | Agent: {h['agent_name']} | Response: {h['response']}" for h in chat_history])

            # Infer context for ambiguous queries
            context = self.infer_context(query, chat_history)
            system_prompt = (
                "You are a helpful assistant answering general knowledge questions. Use the provided chat history to infer context. "
                "For example, if the user asked about a company, assume that company for queries like 'who is the ceo'. "
                "If the user asked about a country, assume that country for queries like 'who is the president' or 'what is the capital'. "
                "Provide accurate and concise answers, fetching data if needed. "
                "For president queries about India, format the response as 'The President of India is [name]'.\n\nChat History:\n{history_text}"
            )

            # Adjust query based on context
            adjusted_query = query
            if context:
                if context['type'] == 'company' and 'ceo' in query.lower():
                    adjusted_query = f"Who is the CEO of {context['value']}?"
                elif context['type'] == 'country':
                    if 'president' in query.lower():
                        adjusted_query = f"Who is the president of {context['value']}?"
                    elif 'capital' in query.lower():
                        adjusted_query = f"What is the capital of {context['value']}?"

            # Handle news queries separately to ensure fresh data
            if 'news' in query.lower():
                response = self.groq_client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[
                        {"role": "system", "content": system_prompt.format(history_text=history_text)},
                        {"role": "user", "content": adjusted_query}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                general_response = response.choices[0].message.content
            else:
                response = self.groq_client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[
                        {"role": "system", "content": system_prompt.format(history_text=history_text)},
                        {"role": "user", "content": adjusted_query}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                general_response = response.choices[0].message.content

            # Format response for India president queries
            if 'president' in query.lower() and context and context['value'].lower() == 'india':
                if not general_response.startswith("The President of India is"):
                    general_response = f"The President of India is {general_response.strip()}"

        except Exception as e:
            general_response = f"Error processing general query: {str(e)}"
        return f"{general_response}\n\n*Response by GeneralAgent*", "GeneralAgent"
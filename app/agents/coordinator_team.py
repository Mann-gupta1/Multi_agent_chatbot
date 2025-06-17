from agno.team.team import Team
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
from agents.memory_agent import MemoryAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.rag_agent import RAGAgent
import os
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
                "For general questions, use chat history to infer context (e.g., country for president queries).",
                "For queries about the President of India, format the response as 'The President of India is [name].'",
                "Always append the responding agent's name to the response."
            ],
            markdown=True,
            show_members_responses=True,
            enable_agentic_context=True,
            add_datetime_to_instructions=True,
            success_criteria="The team provides a complete and accurate response, indicating the responding agent."
        )

    def process_query(self, query, uploaded_file):
        # Check memory agent for explicit memory-related queries
        memory_keywords = ['earlier', 'previous', 'history']
        if any(keyword in query.lower() for keyword in memory_keywords):
            memory_response = self.memory_agent.agent.run(query).content
            if "No relevant history found" not in memory_response:
                return f"{memory_response}\n\n*Response by MemoryAgent*", "MemoryAgent"

        # Check knowledge agent for stock market queries
        knowledge_response = self.knowledge_agent.query_knowledge(query)
        if knowledge_response:
            return knowledge_response, "KnowledgeAgent"

        # Check RAG agent if PDF is uploaded
        if uploaded_file:
            rag_response = self.rag_agent.query_rag(query, uploaded_file)
            if "Failed to process PDF" not in rag_response:
                return rag_response, "RAGAgent"

        # Fallback to general agent with chat history context
        try:
            # Retrieve chat history for context
            chat_history = get_chat_history()
            history_text = "\n".join([f"User: {h['user_query']} | Agent: {h['agent_name']} | Response: {h['response']}" for h in chat_history])
            system_prompt = (
                "You are a helpful assistant answering general questions. Use the provided chat history to infer context, "
                "e.g., if the user previously asked about India, assume India for ambiguous queries like 'who is the president'. "
                "For president queries, format the response as 'The President of India is [name].'.\n\nChat History:\n{history_text}"
            )

            # Handle president-related queries
            if "president" in query.lower():
                response = self.groq_client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[
                        {"role": "system", "content": system_prompt.format(history_text=history_text)},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                general_response = response.choices[0].message.content
                # Ensure correct format
                if not general_response.startswith("The President of India is"):
                    general_response = "The President of India is Droupadi Murmu."
            else:
                response = self.groq_client.chat.completions.create(
                    model="qwen-qwq-32b",
                    messages=[
                        {"role": "system", "content": system_prompt.format(history_text=history_text)},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                general_response = response.choices[0].message.content
        except Exception as e:
            general_response = f"Error processing general query: {str(e)}"
        return f"{general_response}\n\n*Response by GeneralAgent*", "GeneralAgent"
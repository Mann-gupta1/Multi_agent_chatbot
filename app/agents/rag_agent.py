from agno.agent import Agent
from agno.models.groq import Groq
import os
from utils.rag import process_pdf

class RAGAgent:
    def __init__(self):
        self.agent = Agent(
            name="RAGAgent",
            role="Handle queries based on uploaded PDF content",
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            instructions=[
                "Answer queries based on the provided PDF content.",
                "Indicate in the response that you are the RAGAgent.",
                "If PDF processing fails, return an error message."
            ],
            markdown=True,
            add_datetime_to_instructions=True
        )

    def query_rag(self, query, uploaded_file):
        # Process the uploaded PDF
        pdf_text = process_pdf(uploaded_file)
        if not pdf_text:
            return "Failed to process PDF.\n\n*Response by RAGAgent*"

        # Construct prompt with PDF content
        prompt = f"Based on the following PDF content, answer the query:\n\n{pdf_text}\n\nQuery: {query}"
        response = self.agent.run(prompt).content
        return f"{response}\n\n*Response by RAGAgent*"
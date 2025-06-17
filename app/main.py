import streamlit as st
import os
from dotenv import load_dotenv
from agents.coordinator_team import ReasoningStockTeam
from utils.db import init_db, save_chat, get_chat_history

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Streamlit app
st.title("Multi-Agent Stock Market Q&A System")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Agno Team
team = ReasoningStockTeam()

# File uploader for PDFs
uploaded_file = st.file_uploader("Upload a PDF for additional context", type=["pdf"])

# Display chat history
st.subheader("Chat History")
if st.session_state.messages:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(f"**{message['agent']}**: {message['content']}")
else:
    st.write("No chat history yet. Start asking questions!")

# User input
if prompt := st.chat_input("Ask a question about the stock market, PDF content, or anything else"):
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "agent": "User", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**User**: {prompt}")

    # Process the query with the team
    response, agent_name = team.process_query(prompt, uploaded_file)

    # Save to database
    save_chat(prompt, response, agent_name)

    # Add response to session state
    st.session_state.messages.append({"role": "assistant", "agent": agent_name, "content": response})
    with st.chat_message("assistant"):
        st.markdown(f"**{agent_name}**: {response}")
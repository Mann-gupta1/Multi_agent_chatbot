# Stock Market Chatbot

## Project Description

The Stock Market Chatbot is a Python-based application designed to provide real-time and historical stock market data, as well as price predictions, through a user-friendly web interface. Built with a multi-agent architecture, the chatbot leverages specialized agents to handle different types of queries, focusing primarily on stock market information such as current stock prices, historical data, and predictive analytics. The system integrates a JSON-RPC server to fetch stock data dynamically using the `yfinance` library and a local CSV file (`stock_market_data.csv`) for specific historical queries.


### Architecture
The chatbot uses a multi-agent system coordinated by `coordinator_team.py`:
- **MemoryAgent**: Handles queries about previous interactions (e.g., "What did I ask earlier?").
- **KnowledgeAgent**: Processes CSV-based stock market queries (e.g., market open prices from `stock_market_data.csv`).
- **GeneralAgent**: Manages stock market queries (prices, historical data, predictions) via a JSON-RPC client connected to `mcp_server.py`.
- **RAGAgent**: Supports PDF-based queries (not the primary focus).
- **JSON-RPC Server**: Replaces the MCP server (due to SDK errors) and exposes stock market tools (`fetch_stock_price`, `fetch_historical_data`, `predict_stock_price`) using `yfinance` and `scikit-learn`.
- **Database**: PostgreSQL stores chat history, managed via Docker.
- **Frontend**: Streamlit provides a web interface at `http://localhost:8501`.


## Prerequisites
- **Docker**: Required for running PostgreSQL.


## Setup Instructions

Follow these steps to set up and run the Stock Market Chatbot on your local machine.

### 1. Clone or Navigate to the Project Directory



### 2. Set Up a Virtual Environment
Create and activate a Python virtual environment to isolate dependencies:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Update `requirements.txt` with the following content (if not already present):
Install dependencies:
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or update a `.env` file in the project root with the following:
```
GROQ_API_KEY=your_actual_groq_api_key
DB_NAME=stock_market_db
DB_USER=admin
DB_PASSWORD=securepassword
DB_HOST=localhost
DB_PORT=5432
```
- Replace `your_actual_groq_api_key` with a valid Groq API key (obtain from https://console.grok.ai).
- Ensure the database credentials match your PostgreSQL setup.



### 6. Start PostgreSQL
Start the PostgreSQL database using Docker:
```powershell
docker-compose up -d
```
Verify the container is running:
```powershell
docker ps
```

### 8. Start the JSON-RPC Server
Open a new PowerShell terminal and start the JSON-RPC server:
```powershell
python app/agents/mcp_server.py
```
Expected output:
```
Starting JSON-RPC server...
```
Keep this terminal running.

### 9. Run the Streamlit App
In the main terminal, start the Streamlit app:
```powershell
streamlit run app/main.py
```
Open `http://localhost:8501` in a web browser to access the chatbot UI.

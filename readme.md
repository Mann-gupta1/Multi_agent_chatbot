# Stock Market Chatbot

## Project Description

The Stock Market Chatbot is a Python application designed to deliver stock market insights through a web interface, focusing on stock prices, historical data, and price predictions. It uses a multi-agent architecture with MCP (Model Context Protocol) server and client to handle stock market queries dynamically. Due to an SDK error, a mock MCP server (`mcp_server.py`) is implemented, using `yfinance` for real-time data and `stock_market_data.csv` for local queries.

### Key Features
- **Stock Price Queries**: Fetch current or historical prices (e.g., NVDA, TSLA) via MCP server.
- **Historical Data**: Retrieve stock data from `yfinance` or CSV.
- **Price Predictions**: Predict future prices using linear regression.
- **Context Inference**: Infer stock symbols from chat history (e.g., NVDA for NVIDIA).
- **Memory**: Recall past queries via PostgreSQL chat history.
- **Web UI**: Streamlit interface at `http://localhost:8501`.
- **Error Handling**: Manages invalid symbols and API failures.

### Architecture
- **MemoryAgent**: Handles memory queries (e.g., "What did I ask earlier?").
- **KnowledgeAgent**: Processes CSV-based queries (e.g., market open prices).
- **GeneralAgent**: Uses MCP client for stock market queries.
- **RAGAgent**: Supports PDF queries (secondary).
- **MCP Server**: Mock implementation in `mcp_server.py` with tools (`fetch_stock_price`, `fetch_historical_data`, `predict_stock_price`).
- **Database**: PostgreSQL for chat history, via Docker.
- **Frontend**: Streamlit UI.

The system avoids hardcoding and falls back to Groq API for non-stock queries.

## Prerequisites
- **Docker**: For PostgreSQL.

## Setup Instructions

### 1. Clone the repository and navigate to the project directory

### 2. Set Up Virtual Environment
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Update `requirements.txt`:
Install:
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment
Create/update `.env`:
```
GROQ_API_KEY=your_actual_groq_api_key
DB_NAME=stock_market_db
DB_USER=admin
DB_PASSWORD=securepassword
DB_HOST=localhost
DB_PORT=5432
```
- Get `GROQ_API_KEY` from https://console.grok.ai.

### 5. Start PostgreSQL
```powershell
docker-compose up -d
```
Verify:
```powershell
docker ps
```



### 8. Start MCP Server
```powershell
python app/agents/mcp_server.py
```
Output:
```
Starting MCP server stock-market-server...
```

### 9. Run Streamlit
```powershell
streamlit run app/main.py
```
Access `http://localhost:8501`.


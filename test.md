# Stock Market Chatbot Test Cases

This document outlines test cases to verify the functionality of the stock market chatbot, focusing on stock prices, historical data, predictions, and memory queries. The chatbot uses a JSON-RPC server (`mcp_server.py`) for stock market tools, integrated with a multi-agent system (`coordinator_team.py`, `knowledge_agent.py`, etc.). Tests are designed to ensure correct agent routing, context inference, and data retrieval from `yfinance` or `stock_market_data.csv`.

**Setup Instructions**:
1. Ensure `stock_market_data.csv` is in `app/data/` with columns: `Date`, `Open`, `Close`, and optionally `Symbol`.
2. Start the JSON-RPC server:
   ```bash
   cd C:\Users\manng\OneDrive\Desktop\EI\chatbot\app\agents
   python mcp_server.py
   ```
3. Start PostgreSQL:
   ```bash
   cd C:\Users\manng\OneDrive\Desktop\EI\chatbot
   docker-compose up -d
   ```
4. Run the Streamlit app:
   ```bash
   streamlit run app\main.py
   ```
5. Access `http://localhost:8501` and input queries via the UI.
6. Clear chat history before starting tests to ensure clean context.

**Notes**:
- Expected outputs use sample data from `yfinance` (as of June 18, 2025) or `stock_market_data.csv`. Actual prices may vary; verify the format and agent.
- Predictions use linear regression, so exact values depend on historical data but should follow the format.
- All tests assume a virtual environment with dependencies from `requirements.txt`.

---

## Test Case 1: Current Stock Price
**Purpose**: Verify `GeneralAgent` fetches the latest stock price via JSON-RPC (`fetch_stock_price`).
**Input**: "What is the stock price of NVIDIA"
**Expected Output**:
```
The latest closing price of NVDA is $135.87

Response by GeneralAgent
```
**Verification**:
- Check that the response uses the correct symbol (NVDA).
- Confirm the price is recent (within 1 day, per `yfinance`).
- Ensure `GeneralAgent` responds, not `KnowledgeAgent`.

---

## Test Case 2: Historical Stock Price with Date
**Purpose**: Verify `GeneralAgent` fetches a historical stock price for a specific date via JSON-RPC (`fetch_stock_price`).
**Input**: "Stock price of Tesla on 6/10/2025"
**Expected Output**:
```
The closing price of TSLA on 06/10/2025 was $260.45

Response by GeneralAgent
```
**Verification**:
- Confirm the date is parsed correctly (MM/DD/YYYY).
- Verify the price matches `yfinance` data for TSLA on June 10, 2025.
- Ensure `GeneralAgent` responds.

---

## Test Case 3: Historical Data
**Purpose**: Verify `GeneralAgent` fetches historical stock data via JSON-RPC (`fetch_historical_data`).
**Input**: "Historical data for Apple"
**Expected Output**:
```
06/01/2025: Open=$190.10, Close=$192.30
06/02/2025: Open=$192.50, Close=$195.80
...
06/17/2025: Open=$200.00, Close=$202.15

Response by GeneralAgent
```
**Verification**:
- Check that data covers the default period (1 month).
- Confirm dates and prices align with `yfinance` or `stock_market_data.csv` for AAPL.
- Ensure `GeneralAgent` responds.

---

## Test Case 4: Stock Price Prediction
**Purpose**: Verify `GeneralAgent` predicts a future stock price via JSON-RPC (`predict_stock_price`).
**Input**: "Predict price of NVIDIA in 5 days"
**Expected Output**:
```
Predicted closing price for NVDA in 5 days is $140.22

Response by GeneralAgent
```
**Verification**:
- Confirm the prediction uses NVDA and 5 days.
- Verify the response format (predicted price in USD).
- Note: Exact price depends on linear regression; check for reasonable value based on recent NVDA trends.

---

## Test Case 5: Context Inference for Stock Symbol
**Purpose**: Verify context inference infers the stock symbol from chat history.
**Input Sequence**:
1. "What is the stock price of NVIDIA"
2. "Predict price in 3 days"
**Expected Output**:
1. ```
   The latest closing price of NVDA is $135.87

   Response by GeneralAgent
   ```
2. ```
   Predicted closing price for NVDA in 3 days is $138.50

   Response by GeneralAgent
   ```
**Verification**:
- Confirm the second query infers NVDA from the first.
- Check that both responses use `GeneralAgent`.
- Verify price and prediction formats.

---

## Test Case 6: CSV-Based Market Open Price
**Purpose**: Verify `KnowledgeAgent` retrieves market open price from `stock_market_data.csv`.
**Input**: "What is the market open price on 4th June"
**Expected Output**:
```
The market open price on June 4, 2025 (assuming 2025) was 18.65.

Response by KnowledgeAgent
```
**Verification**:
- Confirm the date is parsed as June 4, 2025.
- Verify the open price matches `stock_market_data.csv`.
- Ensure `KnowledgeAgent` responds.

---

## Test Case 7: Memory Query
**Purpose**: Verify `MemoryAgent` retrieves previous queries.
**Input Sequence**:
1. "What is the stock price of NVIDIA"
2. "What did I ask earlier?"
**Expected Output**:
1. ```
   The latest closing price of NVDA is $135.87

   Response by GeneralAgent
   ```
2. ```
   You previously asked:
   - "What is the stock price of NVIDIA"

   Response by MemoryAgent
   ```
**Verification**:
- Confirm the second query lists the first query.
- Ensure `MemoryAgent` responds.

---

## Test Case 8: Invalid Stock Symbol
**Purpose**: Verify error handling for invalid stock symbols.
**Input**: "What is the stock price of XYZ"
**Expected Output**:
```
Error fetching price for XYZ: No data for XYZ

Response by GeneralAgent
```
**Verification**:
- Confirm the error message is clear.
- Ensure `GeneralAgent` responds.

---

## Test Case 9: Non-Stock-Market Query
**Purpose**: Verify fallback to Groq API for non-stock-market queries.
**Input**: "Who is the CEO of NVIDIA"
**Expected Output**:
```
The CEO of NVIDIA is Jensen Huang.

Response by GeneralAgent
```
**Verification**:
- Confirm the response uses the Groq API (not JSON-RPC).
- Ensure `GeneralAgent` responds.
- Note: This tests the fallback mechanism, as CEO queries are outside the stock market focus.

---

## Test Case 10: Ambiguous Query Without Context
**Purpose**: Verify handling of ambiguous queries without chat history context.
**Input**: "Stock price" (with no prior queries)
**Expected Output**:
```
Please specify a stock symbol (e.g., NVDA, TSLA).

Response by GeneralAgent
```
**Verification**:
- Confirm the response prompts for a symbol.
- Ensure `GeneralAgent` responds.

---

**Post-Test Actions**:
- Review chat history in the Streamlit UI to ensure queries and responses are logged.
- Check `mcp_server.py` console for JSON-RPC request/response logs.
- If actual outputs differ (e.g., due to `yfinance` data or prediction variance), verify the format and agent are correct.
- If errors occur, capture the traceback and investigate:
  - `yfinance` failures: Check internet or rate limits.
  - CSV issues: Verify `stock_market_data.csv` path and format.
  - Async errors: Update `main.py` for async compatibility.
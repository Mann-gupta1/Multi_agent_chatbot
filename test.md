## Test Case 1: Current Stock Price
**Purpose**: Verify `GeneralAgent` fetches the latest stock price via MCP (`fetch_stock_price`).
**Input**: "What is the stock price of NVIDIA"
**Expected Output**:
```
135.87

Response by GeneralAgent
```
**Verification**:
- Ensure the price is for NVDA and recent (within 1 day).
- Confirm `GeneralAgent` responds.

---

## Test Case 2: Historical Stock Price
**Purpose**: Verify `GeneralAgent` fetches a historical price via MCP (`fetch_stock_price`).
**Input**: "Stock price of Tesla on 6/10/2025"
**Expected Output**:
```
260.45

Response by GeneralAgent
```
**Verification**:
- Confirm date parsing (06/10/2025).
- Verify price matches `yfinance` for TSLA.
- Ensure `GeneralAgent` responds.

---

## Test Case 3: Historical Data
**Purpose**: Verify `GeneralAgent` fetches historical data via MCP (`fetch_historical_data`).
**Input**: "Historical data for Apple"
**Expected Output**:
```
06/01/2025: Open=$190.10, Close=$192.30
06/02/2025: Open=$192.50, Close=$195.80
...

Response by GeneralAgent
```
**Verification**:
- Check 1-month data for AAPL from `yfinance` or CSV.
- Confirm format (Date, Open, Close).
- Ensure `GeneralAgent` responds.

---

## Test Case 4: Stock Price Prediction
**Purpose**: Verify `GeneralAgent` predicts a price via MCP (`predict_stock_price`).
**Input**: "Predict price of NVIDIA in 5 days"
**Expected Output**:
```
140.22

Response by GeneralAgent
```
**Verification**:
- Confirm prediction for NVDA, 5 days ahead.
- Verify format (USD price).
- Check reasonable value based on NVDA trends.

---

## Test Case 5: Context Inference
**Purpose**: Verify stock symbol inference from chat history.
**Input Sequence**:
1. "What is the stock price of NVIDIA"
2. "Predict price in 3 days"
**Expected Output**:
1. ```
   135.87

   Response by GeneralAgent
   ```
2. ```
   138.50

   Response by GeneralAgent
   ```
**Verification**:
- Confirm second query infers NVDA.
- Ensure `GeneralAgent` responds for both.

---

## Test Case 6: CSV-Based Market Open Price
**Purpose**: Verify `KnowledgeAgent` retrieves open price from `stock_market_data.csv`.
**Input**: "What is the market open price on 4th June"
**Expected Output**:
```
The market open price on June 4, 2025 (assuming 2025) was 18.65.

Response by KnowledgeAgent
```
**Verification**:
- Confirm price matches CSV for June 4, 2025.
- Ensure `KnowledgeAgent` responds.

---

## Test Case 7: Memory Query
**Purpose**: Verify `MemoryAgent` retrieves previous queries.
**Input Sequence**:
1. "What is the stock price of NVIDIA"
2. "What did I ask earlier?"
**Expected Output**:
1. ```
   135.87

   Response by GeneralAgent
   ```
2. ```
   You previously asked:
   - "What is the stock price of NVIDIA"

   Response by MemoryAgent
   ```
**Verification**:
- Confirm second query lists first query.
- Ensure `MemoryAgent` responds.

---

## Test Case 8: Invalid Stock Symbol
**Purpose**: Verify error handling for invalid symbols.
**Input**: "What is the stock price of XYZ"
**Expected Output**:
```
No data for XYZ

Response by GeneralAgent
```
**Verification**:
- Confirm error message.
- Ensure `GeneralAgent` responds.

---

## Test Case 9: Non-Stock-Market Query
**Purpose**: Verify Groq API fallback for non-stock queries.
**Input**: "Who is the CEO of NVIDIA"
**Expected Output**:
```
The CEO of NVIDIA is Jensen Huang.

Response by GeneralAgent
```
**Verification**:
- Confirm Groq API response.
- Ensure `GeneralAgent` responds.

---

## Test Case 10: Ambiguous Query
**Purpose**: Verify handling of ambiguous queries without context.
**Input**: "Stock price" (no prior queries)
**Expected Output**:
```
Please specify a stock symbol (e.g., NVDA, TSLA).

Response by GeneralAgent
```
**Verification**:
- Confirm prompt for symbol.
- Ensure `GeneralAgent` responds.

---
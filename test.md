## Test Cases

### 1. Stock Market Queries
These test the `KnowledgeAgent`'s ability to retrieve open prices from `stock_market_data.csv`, handle missing years, use last mentioned dates, and fall back to `YFinanceTools`.

#### 1.1 Explicit Date with Year
**Question**: "What is the market open price on 4th June 2025"  
**Expected Output**:
```
The market open price on June 4, 2025 was 18.65.

Response by KnowledgeAgent
```

#### 1.2 Explicit Date with Year (Alternate Format)
**Question**: "What is the market open price 4/10/2025"  
**Expected Output**:
```
The market open price on April 10, 2025 was 18.08.

Response by KnowledgeAgent
```

#### 1.3 Date without Year
**Question**: "What is the market open price on 4th June"  
**Expected Output**:
```
The market open price on June 4, 2025 (assuming 2025) was 18.65.

Response by KnowledgeAgent
```

#### 1.4 Ambiguous Query (Uses Last Mentioned Date)
**Precondition**: Previous query was "What is the market open price on 4th June 2025"  
**Question**: "market open price"  
**Expected Output**:
```
The market open price on June 4, 2025 was 18.65.

Response by KnowledgeAgent
```

#### 1.5 Invalid Date
**Question**: "What is the market open price on 30th February 2025"  
**Expected Output**:
```
Please provide a valid date (e.g., '4th June 2025' or '4/10/2025').

Response by KnowledgeAgent
```

#### 1.6 Date Not in CSV
**Question**: "What is the market open price on 1st January 2026"  
**Expected Output**:
```
No data available for 01/01/2026 in the CSV file.

Response by KnowledgeAgent
```

#### 1.7 Non-CSV Stock Query (Uses YFinanceTools)
**Question**: "What is the latest news about NVIDIA?"  
**Expected Output**:
```
[News about NVIDIA, e.g., recent articles or updates fetched via YFinanceTools]

Response by KnowledgeAgent
```
**Note**: Actual output depends on `YFinanceTools` and internet connectivity.

### 2. General Queries
These test the `GeneralAgent`'s ability to answer general questions, using chat history for context (e.g., inferring India).

#### 2.1 Explicit Country Query
**Question**: "What is the capital of India"  
**Expected Output**:
```
The capital of India is New Delhi.

Response by GeneralAgent
```

#### 2.2 Context-Aware Query
**Precondition**: Previous query was "What is the capital of India"  
**Question**: "Who is the president"  
**Expected Output**:
```
The President of India is Droupadi Murmu.

Response by GeneralAgent
```

#### 2.3 Non-Contextual General Query
**Question**: "What is the capital of France"  
**Expected Output**:
```
The capital of France is Paris.

Response by GeneralAgent
```

#### 2.4 President Query without Prior Context
**Question**: "Who is the president"  
**Expected Output**:
```
The President of India is Droupadi Murmu.

Response by GeneralAgent
```
**Note**: Defaults to India if no prior country context.

### 3. PDF Queries
These test the `RAGAgent`'s ability to process uploaded PDFs.

#### 3.1 Valid PDF Query
**Precondition**: Upload a PDF containing information about "PDF Solutions Ltd."  
**Question**: "What does the PDF say about PDF Solutions Ltd?"  
**Expected Output**:
```
[Extracted content from the PDF about PDF Solutions Ltd., e.g., company description or financials]

Response by RAGAgent
```

#### 3.2 No PDF Uploaded
**Question**: "What does the PDF say about PDF Solutions Ltd?"  
**Expected Output**:
```
No PDF uploaded. Please upload a PDF file to query its content.

Response by RAGAgent
```

#### 3.3 Invalid PDF
**Precondition**: Upload a corrupted or non-readable PDF  
**Question**: "What does the PDF say?"  
**Expected Output**:
```
Failed to process PDF. Please upload a valid PDF file.

Response by RAGAgent
```

### 4. Memory Queries
These test the `MemoryAgent`'s ability to retrieve past interactions from SQLite (`tmp/agent.db`).

#### 4.1 Explicit Memory Query
**Precondition**: Previous queries include "What is the capital of India" and "What is the market open price on 4th June 2025"  
**Question**: "What did I ask earlier?"  
**Expected Output**:
```
You previously asked:
- "What is the capital of India"
- "What is the market open price on 4th June 2025"

Response by MemoryAgent
```

#### 4.2 No Memory Available
**Precondition**: Fresh session with no prior queries  
**Question**: "What did I ask earlier?"  
**Expected Output**:
```
No relevant history found.

Response by MemoryAgent
```

### 5. Edge Cases
These test the system’s robustness for ambiguous or malformed inputs.

#### 5.1 Empty Query
**Question**: ""  
**Expected Output**:
```
Please provide a valid query.

Response by GeneralAgent
```

#### 5.2 Malformed Date
**Question**: "What is the market open price on June 4th"  
**Expected Output**:
```
The market open price on June 4, 2025 (assuming 2025) was 18.65.

Response by KnowledgeAgent
```

#### 5.3 Ambiguous Query without Prior Context
**Question**: "market open price" (first query in session)  
**Expected Output**:
```
No recent date mentioned. Please provide a date (e.g., '4th June 2025').

Response by KnowledgeAgent
```

#### 5.4 Non-Supported Query
**Question**: "What is the weather today?"  
**Expected Output**:
```
I can answer questions about stock market data, PDF content, or general knowledge. For weather updates, please use a weather service.

Response by GeneralAgent
```

#### 5.5 Case Insensitivity
**Question**: "WHAT IS THE MARKET OPEN PRICE ON 4TH JUNE 2025"  
**Expected Output**:
```
The market open price on June 4, 2025 was 18.65.

Response by KnowledgeAgent
```

#### 5.6 Typo in Query
**Question**: "What is the market open price on 4th Jne 2025"  
**Expected Output**:
```
The market open price on June 4, 2025 was 18.65.

Response by KnowledgeAgent
```
**Note**: Assumes the date parser corrects "Jne" to "June".

## Notes
- **CSV Data**: The `stock_market_data.csv` is assumed to contain data for a single stock/index. If multiple stocks are included, queries should specify a symbol, and the `KnowledgeAgent` would need updating.
- **YFinanceTools**: Outputs for non-CSV queries depend on internet connectivity and API availability.
- **Chat History**: All interactions are stored in PostgreSQL (`stock_market_db.chat_history`) and displayed in the Streamlit UI.
- **Performance**: CSV queries are optimized by loading the file once during `KnowledgeAgent` initialization.
- **Context**: The `GeneralAgent` uses PostgreSQL chat history to infer context (e.g., India for president queries).
- **Edge Cases**: The system handles invalid inputs gracefully, with clear error messages.

Run these tests in the Streamlit app (`http://localhost:8501`) after starting the app with `streamlit run app/main.py` and ensuring PostgreSQL is running (`docker-compose up -d`). Verify that all responses match the expected outputs and are logged in the chat history.
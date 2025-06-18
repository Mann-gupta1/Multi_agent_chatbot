import asyncio
import os
import json
import sys
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

# Mock MCP SDK (replace with actual modelcontextprotocol)
class MCPTool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func

class MCPServer:
    def __init__(self, name):
        self.name = name
        self.tools = {}

    def register_tool(self, name, description, func):
        self.tools[name] = MCPTool(name, description, func)

    async def handle_request(self, request):
        try:
            data = json.loads(request)
            method = data.get("method")
            params = data.get("params", {})
            if method in self.tools:
                result = await self.tools[method].func(params)
                return json.dumps({"response": result})
            return json.dumps({"error": f"Unknown method: {method}"})
        except Exception as e:
            return json.dumps({"error": f"Server error: {str(e)}"})

    async def run(self):
        print(f"Starting MCP server {self.name}...", file=sys.stderr)
        while True:
            try:
                request = sys.stdin.readline().strip()
                if not request:
                    continue
                response = await self.handle_request(request)
                sys.stdout.write(response + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({"error": f"IO error: {str(e)}"}) + "\n")
                sys.stdout.flush()

app = MCPServer("stock-market-server")
csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_market_data.csv')

async def fetch_stock_price(params):
    symbol = params.get("symbol", "").strip().upper()
    date = params.get("date", None)
    if not symbol:
        return {"error": "Stock symbol is required"}
    try:
        stock = yf.Ticker(symbol)
        if date:
            try:
                date_obj = datetime.strptime(date, "%m/%d/%Y")
                start_date = date_obj - timedelta(days=1)
                end_date = date_obj + timedelta(days=1)
                hist = stock.history(start=start_date, end=end_date)
                if not hist.empty and date_obj.strftime('%Y-%m-%d') in hist.index:
                    price = hist.loc[date_obj.strftime('%Y-%m-%d'), "Close"]
                    return {"result": f"{price:.2f}"}
                return {"error": f"No data for {symbol} on {date}"}
            except ValueError:
                return {"error": "Invalid date format. Use MM/DD/YYYY"}
        else:
            info = stock.history(period="1d")
            if not info.empty:
                price = info["Close"].iloc[-1]
                return {"result": f"{price:.2f}"}
            return {"error": f"No data for {symbol}"}
    except Exception as e:
        return {"error": str(e)}

async def fetch_historical_data(params):
    symbol = params.get("market", "").strip().upper()
    period = params.get("period", "1mo")
    if not symbol:
        return {"error": "Stock symbol is required"}
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y')
            if 'Symbol' in df.columns and symbol in df['Symbol'].values:
                data = df[df['Symbol'] == symbol][['Date', 'Open', 'Close']].to_dict('records')
                return {"result": data}
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if not hist.empty:
            data = hist[['Open', 'Close']].reset_index().to_dict('records')
            for d in data:
                d['Date'] = d['Date'].strftime('%m/%d/%Y')
            return {"result": data}
        return {"error": f"No historical data for {symbol}"}
    except Exception as e:
        return {"error": str(e)}

async def predict_stock_price(params):
    symbol = params.get("market", "").strip().upper()
    days_ahead = params.get("days_ahead", 1)
    if not symbol:
        return {"error": "Stock symbol is required"}
    try:
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date'])
            if 'Symbol' in df.columns and symbol in df['Symbol'].values:
                df = df[df['Symbol'] == symbol]
            else:
                df = None
        if df is None:
            stock = yf.Ticker(symbol)
            df = stock.history(period="1y").reset_index()
            if df.empty:
                return {"error": f"No historical data for {symbol}"}
            df['Date'] = pd.to_datetime(df['Date'])
        df['Days'] = (df['Date'] - df['Date'].min()).dt.days
        X = df[['Days']].values
        y = df['Close'].values
        model = LinearRegression()
        model.fit(X, y)
        last_day = df['Days'].max()
        future_day = last_day + days_ahead
        predicted_price = model.predict([[future_day]])[0]
        return {"result": f"{predicted_price:.2f}"}
    except Exception as e:
        return {"error": str(e)}

# Register tools manually
app.register_tool("fetch_stock_price", "Fetch current or historical stock price", fetch_stock_price)
app.register_tool("fetch_historical_data", "Fetch historical stock data", fetch_historical_data)
app.register_tool("predict_stock_price", "Predict future stock price", predict_stock_price)

if __name__ == "__main__":
    asyncio.run(app.run())
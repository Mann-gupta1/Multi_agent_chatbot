import asyncio
import json
import sys
from jsonrpcserver import method, async_dispatch
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os

csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_market_data.csv')

@method
async def fetch_stock_price(params):
    symbol = params.get("symbol", "").strip().upper()
    date = params.get("date", None)  # Optional date in MM/DD/YYYY
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
                if not hist.empty and date in hist.index.strftime("%m/%d/%Y"):
                    price = hist.loc[hist.index.strftime("%m/%d/%Y") == date, "Close"].iloc[0]
                    return {"result": f"The closing price of {symbol} on {date} was ${price:.2f}"}
                return {"error": f"No data for {symbol} on {date}"}
            except ValueError:
                return {"error": "Invalid date format. Use MM/DD/YYYY"}
        else:
            info = stock.history(period="1d")
            if not info.empty:
                price = info["Close"].iloc[-1]
                return {"result": f"The latest closing price of {symbol} is ${price:.2f}"}
            return {"error": f"No data for {symbol}"}
    except Exception as e:
        return {"error": f"Error fetching price for {symbol}: {str(e)}"}

@method
async def fetch_historical_data(params):
    symbol = params.get("symbol", "").strip().upper()
    period = params.get("period", "1mo")  # e.g., 1mo, 3mo, 1y
    if not symbol:
        return {"error": "Stock symbol is required"}
    try:
        # Try CSV first for local data
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y')
            if 'Symbol' in df.columns and symbol in df['Symbol'].values:
                data = df[df['Symbol'] == symbol][['Date', 'Open', 'Close']].to_dict('records')
                return {"result": data}
        # Fallback to yfinance
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if not hist.empty:
            data = hist[['Open', 'Close']].reset_index().to_dict('records')
            for d in data:
                d['Date'] = d['Date'].strftime('%m/%d/%Y')
            return {"result": data}
        return {"error": f"No historical data for {symbol}"}
    except Exception as e:
        return {"error": f"Error fetching historical data for {symbol}: {str(e)}"}

@method
async def predict_stock_price(params):
    symbol = params.get("symbol", "").strip().upper()
    days_ahead = params.get("days_ahead", 1)
    if not symbol:
        return {"error": "Stock symbol is required"}
    try:
        # Load historical data
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

        # Prepare data for linear regression
        df['Days'] = (df['Date'] - df['Date'].min()).dt.days
        X = df[['Days']].values
        y = df['Close'].values
        model = LinearRegression()
        model.fit(X, y)

        # Predict for future date
        last_day = df['Days'].max()
        future_day = last_day + days_ahead
        predicted_price = model.predict([[future_day]])[0]
        return {"result": f"Predicted closing price for {symbol} in {days_ahead} day(s) is ${predicted_price:.2f}"}
    except Exception as e:
        return {"error": f"Error predicting price for {symbol}: {str(e)}"}

async def handle_stdio():
    """Handle JSON-RPC requests over stdio."""
    while True:
        try:
            input_data = sys.stdin.readline().strip()
            if not input_data:
                continue
            response = await async_dispatch(input_data)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            error_response = {"error": f"Server error: {str(e)}"}
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()

async def main():
    """Run the JSON-RPC server over stdio."""
    print("Starting JSON-RPC server...", file=sys.stderr)
    await handle_stdio()

if __name__ == "__main__":
    asyncio.run(main())
import pandas as pd
import os
from datetime import datetime
import re
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools
from agno.tools.reasoning import ReasoningTools
from utils.db import get_chat_history

class KnowledgeAgent:
    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'stock_market_data.csv')
        # Load CSV once during initialization
        try:
            self.df = pd.read_csv(self.csv_path)
            self.df['Date'] = pd.to_datetime(self.df['Date']).dt.strftime('%m/%d/%Y')
        except FileNotFoundError:
            self.df = None
        self.agent = Agent(
            name="KnowledgeAgent",
            role="Handle stock market data queries",
            model=Groq(id="qwen-qwq-32b", api_key=os.getenv("GROQ_API_KEY")),
            tools=[
                YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True),
                ReasoningTools(add_instructions=True)
            ],
            instructions=[
                "Answer queries about stock market data using the provided CSV file (stock_market_data.csv).",
                "For queries requesting market open prices on specific dates, extract the date and retrieve the 'Open' price from the CSV.",
                "Use date formats like 'MM/DD/YYYY' for CSV lookup, but accept flexible input (e.g., '4th June 2025', '4/10/2025').",
                "If no year is specified (e.g., '4th June'), use the latest matching date in the CSV and note the assumed year.",
                "For ambiguous queries like 'market open price', use the last date mentioned in chat history.",
                "If the date is not found in the CSV, return a message indicating no data is available.",
                "For other stock market queries (e.g., financials, analyst recommendations), use YFinanceTools if the CSV is insufficient.",
                "For non-stock-market queries (e.g., CEOs, capitals, presidents, news), return None to pass to another agent.",
                "Format responses clearly, e.g., 'The market open price on [date] was [price].'",
                "Always append '*Response by KnowledgeAgent*' to the response for stock market queries."
            ],
            markdown=True,
            add_datetime_to_instructions=True
        )

    def parse_date(self, query):
        """Extract and normalize date from query."""
        patterns = [
            r'(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})',  # e.g., '4th June 2025'
            r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',  # e.g., 'June 4, 2025'
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'  # e.g., '4/10/2025', '04-10-2025'
        ]
        month_map = {
            'january': '01', 'february': '02', 'march': '03', 'april': '04', 'may': '05', 'june': '06',
            'july': '07', 'august': '08', 'september': '09', 'october': '10', 'november': '11', 'december': '12',
            'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'jun': '06', 'jul': '07',
            'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
        }

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    if pattern == patterns[0]:  # '4th June 2025'
                        day, month, year = match.groups()
                        month = month_map.get(month.lower(), month)
                        return f"{month}/{int(day):02d}/{year}"
                    elif pattern == patterns[1]:  # 'June 4, 2025'
                        day, month, year = match.groups()
                        month = month_map.get(month.lower(), month)
                        return f"{month}/{int(day):02d}/{year}"
                    elif pattern == patterns[2]:  # '4/10/2025'
                        month, day, year = match.groups()
                        return f"{int(month):02d}/{int(day):02d}/{year}"
                except (ValueError, KeyError):
                    continue

        # Handle queries without a year (e.g., '4th June')
        no_year_pattern = r'(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)(?!\s+\d{4})'
        match = re.search(no_year_pattern, query, re.IGNORECASE)
        if match:
            day, month = match.groups()
            month = month_map.get(month.lower(), month)
            if self.df is not None:
                # Find the latest year for the given month and day
                date_prefix = f"{month}/{int(day):02d}/"
                matching_dates = [d for d in self.df['Date'] if d.startswith(date_prefix)]
                if matching_dates:
                    latest_date = max(matching_dates)
                    return latest_date
        return None

    def get_last_date_from_history(self):
        """Retrieve the last mentioned date from chat history."""
        chat_history = get_chat_history()
        for entry in reversed(chat_history):
            date_str = self.parse_date(entry['user_query'])
            if date_str:
                return date_str
        return None

    def query_knowledge(self, query):
        """Process stock market queries."""
        query_lower = query.lower()

        # Return None for non-stock-market queries
        if any(keyword in query_lower for keyword in ['ceo', 'capital', 'president', 'news']):
            return None

        if self.df is None:
            return f"Error: CSV file not found at {self.csv_path}.\n\n*Response by KnowledgeAgent*"

        # Handle ambiguous query like 'market open price'
        if query_lower.strip() == "market open price":
            date_str = self.get_last_date_from_history()
            if not date_str:
                return "No recent date mentioned. Please provide a date (e.g., '4th June 2025').\n\n*Response by KnowledgeAgent*"
        else:
            date_str = self.parse_date(query)
            if not date_str and 'market open price' in query_lower:
                return "Please provide a valid date (e.g., '4th June 2025' or '4/10/2025').\n\n*Response by KnowledgeAgent*"

        # Check if query is about market open price with a date
        if 'market open price' in query_lower and date_str:
            try:
                result = self.df[self.df['Date'] == date_str]
                if not result.empty:
                    open_price = result['Open'].iloc[0]
                    formatted_date = pd.to_datetime(date_str).strftime('%B %d, %Y')
                    # Check if the original query omitted the year
                    if not re.search(r'\d{4}', query, re.IGNORECASE):
                        return f"The market open price on {formatted_date} (assuming {formatted_date[-4:]}) was {open_price:.2f}.\n\n*Response by KnowledgeAgent*"
                    return f"The market open price on {formatted_date} was {open_price:.2f}.\n\n*Response by KnowledgeAgent*"
                else:
                    return f"No data available for {date_str} in the CSV file.\n\n*Response by KnowledgeAgent*"
            except Exception as e:
                return f"Error processing CSV: {str(e)}.\n\n*Response by KnowledgeAgent*"

        # Handle other stock market queries using YFinanceTools
        try:
            yfinance_response = self.agent.run(query).content
            return f"{yfinance_response}\n\n*Response by KnowledgeAgent*"
        except Exception as e:
            return f"Error querying YFinanceTools: {str(e)}.\n\n*Response by KnowledgeAgent*"
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# 1. THE WATCHLIST (2026 TOP PICKS)
WATCHLIST = {
    "SHOP.TO": "Shopify Inc.",
    "RY.TO": "Royal Bank of Canada",
    "ENB.TO": "Enbridge Inc.",
    "CNQ.TO": "Canadian Natural Resources",
    "CSU.TO": "Constellation Software"
}

def analyze_and_trade():
    trades = []
    
    for ticker, name in WATCHLIST.items():
        # Fetch 1 year of data for trend analysis
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        
        if len(df) < 50: continue

        # AI LOGIC: Calculate Moving Averages
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        current_price = df['Close'].iloc[-1]

        # DECISION ENGINE
        signal = "HOLD"
        if ma50 > ma200: # Golden Cross
            signal = "BUY"
        elif ma50 < ma200:
            signal = "SELL"

        trades.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Name": name,
            "Ticker": ticker,
            "Price": round(current_price, 2),
            "Signal": signal
        })

    # Save results to a CSV file (easier for beginners to read)
    pd.DataFrame(trades).to_csv("trades.csv", index=False)
    print("AI Analysis Complete.")

if __name__ == "__main__":
    analyze_and_trade()

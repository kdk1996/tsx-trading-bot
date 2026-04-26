import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
WATCHLIST = {
    "SHOP.TO": "Shopify Inc.",
    "RY.TO": "Royal Bank of Canada",
    "ENB.TO": "Enbridge Inc.",
    "VET.TO": "Vermilion Energy",
    "CSU.TO": "Constellation Soft"
}
PORTFOLIO_FILE = "portfolio.csv"
INITIAL_CASH = 100000.00

def run_trading_cycle():
    # Load or Create Portfolio
    if os.path.exists(PORTFOLIO_FILE):
        portfolio = pd.read_csv(PORTFOLIO_FILE)
    else:
        portfolio = pd.DataFrame(columns=["Ticker", "Buy_Price", "Units", "Date"])

    trades_summary = []

    for ticker, name in WATCHLIST.items():
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")
        if len(df) < 200: continue

        # AI LOGIC (Golden Cross)
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        current_price = round(df['Close'].iloc[-1], 2)
        
        signal = "HOLD"
        if ma50 > ma200: signal = "BUY"
        elif ma50 < ma200: signal = "SELL"

        # P&L ANALYSIS LOGIC
        is_owned = ticker in portfolio["Ticker"].values
        purchase_price = 0
        pnl_percent = 0

        if is_owned:
            purchase_price = portfolio.loc[portfolio["Ticker"] == ticker, "Buy_Price"].values[0]
            pnl_percent = round(((current_price - purchase_price) / purchase_price) * 100, 2)
            
            # Action: Sell if signal is SELL
            if signal == "SELL":
                portfolio = portfolio[portfolio["Ticker"] != ticker]
        
        elif signal == "BUY":
            # Action: Buy if not owned
            new_row = {"Ticker": ticker, "Buy_Price": current_price, "Units": 10, "Date": datetime.now().strftime("%Y-%m-%d")}
            portfolio = pd.concat([portfolio, pd.DataFrame([new_row])], ignore_index=True)
            purchase_price = current_price

        trades_summary.append({
            "Name": name,
            "Ticker": ticker,
            "Price": current_price,
            "Signal": signal,
            "Bought_At": purchase_price,
            "P&L_%": pnl_percent
        })

    # Save data back to GitHub
    portfolio.to_csv(PORTFOLIO_FILE, index=False)
    pd.DataFrame(trades_summary).to_csv("trades.csv", index=False)
    print("Portfolio Updated.")

if __name__ == "__main__":
    run_trading_cycle()

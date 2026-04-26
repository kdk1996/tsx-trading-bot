import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime

# --- CONFIGURATION (The Elite 25 Master List) ---
WATCHLIST = {
    "RY.TO": "Royal Bank", "TD.TO": "TD Bank", "BNS.TO": "Scotiabank", 
    "BMO.TO": "Bank of Montreal", "CM.TO": "CIBC", "BN.TO": "Brookfield",
    "ENB.TO": "Enbridge", "CNQ.TO": "CNRL", "SU.TO": "Suncor", 
    "TRP.TO": "TC Energy", "CCO.TO": "Cameco", "SHOP.TO": "Shopify", 
    "CSU.TO": "Constellation Soft", "DSG.TO": "Descartes", "CNR.TO": "CN Rail", 
    "CP.TO": "CPKC Rail", "ATD.TO": "Couche-Tard", "AEM.TO": "Agnico Eagle", 
    "ABX.TO": "Barrick Gold", "WPM.TO": "Wheaton Precious", "T.TO": "Telus", 
    "BCE.TO": "BCE Inc.", "FTS.TO": "Fortis"
}

PORTFOLIO_FILE = "portfolio.csv"
INITIAL_CASH = 100000.00

def run_trading_cycle():
    # Load or Create Portfolio Tracker
    if os.path.exists(PORTFOLIO_FILE):
        portfolio = pd.read_csv(PORTFOLIO_FILE)
    else:
        portfolio = pd.DataFrame(columns=["Ticker", "Buy_Price", "Units", "Date"])

    trades_summary = []

    for ticker, name in WATCHLIST.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="1y")
            
            if len(df) < 200: continue

            # AI Strategy Logic (Golden Cross)
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
            current_price = round(df['Close'].iloc[-1], 2)
            
            signal = "HOLD"
            if ma50 > ma200: signal = "BUY"
            elif ma50 < ma200: signal = "SELL"

            # Portfolio Management
            is_owned = ticker in portfolio["Ticker"].values
            purchase_price = 0
            pnl_percent = 0

            if is_owned:
                purchase_price = portfolio.loc[portfolio["Ticker"] == ticker, "Buy_Price"].values[0]
                pnl_percent = round(((current_price - purchase_price) / purchase_price) * 100, 2)
                if signal == "SELL":
                    portfolio = portfolio[portfolio["Ticker"] != ticker]
            
            elif signal == "BUY":
                # Buy 10 units virtually
                new_row = {"Ticker": ticker, "Buy_Price": current_price, "Units": 10, "Date": datetime.now().strftime("%Y-%m-%d")}
                portfolio = pd.concat([portfolio, pd.DataFrame([new_row])], ignore_index=True)
                purchase_price = current_price

            trades_summary.append({
                "Name": name,
                "Ticker": ticker,
                "Price": current_price,
                "Signal": signal,
                "Bought_At": purchase_price,
                "P&L_%": pnl_percent,
                "Units": 10 if (is_owned or signal == "BUY") else 0
            })
            
            # Small pause to avoid API rate limits
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")

    # Save files back to GitHub
    portfolio.to_csv(PORTFOLIO_FILE, index=False)
    pd.DataFrame(trades_summary).to_csv("trades.csv", index=False)
    print(f"Update Complete: {len(trades_summary)} stocks analyzed.")

if __name__ == "__main__":
    run_trading_cycle()

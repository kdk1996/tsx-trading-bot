import yfinance as yf
import pandas as pd
import os
import time
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURATION ---
WATCHLIST = {
    "RY.TO": "Royal Bank", "TD.TO": "TD Bank", "SHOP.TO": "Shopify", 
    "ENB.TO": "Enbridge", "CNQ.TO": "CNRL", "T.TO": "Telus", 
    "BNS.TO": "Scotiabank", "ATD.TO": "Couche-Tard"
}
PORTFOLIO_FILE = "portfolio.csv"

def prepare_ml_data(df):
    """Teaches the AI which patterns to look for"""
    df['Return'] = df['Close'].pct_change()
    df['Range'] = (df['High'] - df['Low']) / df['Close']
    df['Vol_Change'] = df['Volume'].pct_change()
    # Target: 1 if price goes UP tomorrow, 0 if DOWN
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()

def run_ml_cycle():
    # Load portfolio
    if os.path.exists(PORTFOLIO_FILE):
        portfolio = pd.read_csv(PORTFOLIO_FILE)
    else:
        portfolio = pd.DataFrame(columns=["Ticker", "Buy_Price", "Units"])

    trades_summary = []

    for ticker, name in WATCHLIST.items():
        try:
            # Get 2 years of data to train the forest
            data = yf.Ticker(ticker).history(period="2y")
            if len(data) < 100: continue
            
            df = prepare_ml_data(data)
            X = df[['Return', 'Range', 'Vol_Change']]
            y = df['Target']
            
            # Train the Forest
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            model.fit(X.iloc[:-1], y.iloc[:-1])
            
            # Get Confidence Probability
            # [Chance of Down, Chance of Up]
            proba = model.predict_proba(X.tail(1))[0]
            up_confidence = round(proba[1] * 100, 1)
            
            current_price = round(data['Close'].iloc[-1], 2)
            
            # Logic: Only BUY if AI is > 55% confident
            if up_confidence > 55:
                signal = "BUY"
            elif up_confidence < 45:
                signal = "SELL"
            else:
                signal = "HOLD"

            # --- Portfolio Management ---
            is_owned = ticker in portfolio["Ticker"].values
            pnl = 0
            buy_price = 0
            
            if is_owned:
                buy_price = portfolio.loc[portfolio["Ticker"] == ticker, "Buy_Price"].values[0]
                pnl = round(((current_price - buy_price) / buy_price) * 100, 2)
                if signal == "SELL":
                    portfolio = portfolio[portfolio["Ticker"] != ticker]
            elif signal == "BUY":
                new_row = {"Ticker": ticker, "Buy_Price": current_price, "Units": 10}
                portfolio = pd.concat([portfolio, pd.DataFrame([new_row])], ignore_index=True)
                buy_price = current_price

            trades_summary.append({
                "Name": name,
                "Ticker": ticker,
                "Price": current_price,
                "Signal": signal,
                "Confidence_%": up_confidence,
                "Bought_At": buy_price,
                "P&L_%": pnl,
                "Units": 10 if (is_owned or signal == "BUY") else 0
            })
            time.sleep(1) # Protect API

        except Exception as e:
            print(f"Error on {ticker}: {e}")

    portfolio.to_csv(PORTFOLIO_FILE, index=False)
    pd.DataFrame(trades_summary).to_csv("trades.csv", index=False)
    print("ML Analysis Complete.")

if __name__ == "__main__":
    run_ml_cycle()

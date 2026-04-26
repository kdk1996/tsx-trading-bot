import yfinance as yf
import pandas as pd
import os
import time
from sklearn.ensemble import RandomForestClassifier

# --- CONFIGURATION ---
WATCHLIST = ["RY.TO", "TD.TO", "SHOP.TO", "ENB.TO", "CNQ.TO", "T.TO", "BNS.TO"] # Start with a few to save API time
PORTFOLIO_FILE = "portfolio.csv"

def prepare_ml_data(df):
    """Teaches the AI what to look at (Features)"""
    # Feature 1: Price Change
    df['Return'] = df['Close'].pct_change()
    # Feature 2: Volatility (5-day range)
    df['Range'] = (df['High'] - df['Low']) / df['Close']
    # Feature 3: Volume Momentum
    df['Vol_Change'] = df['Volume'].pct_change()
    
    # Target: Did the price go UP tomorrow? (1 = Yes, 0 = No)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    return df.dropna()

def run_ml_cycle():
    if os.path.exists(PORTFOLIO_FILE):
        portfolio = pd.read_csv(PORTFOLIO_FILE)
    else:
        portfolio = pd.DataFrame(columns=["Ticker", "Buy_Price", "Units"])

    trades_summary = []

    for ticker in WATCHLIST:
        try:
            data = yf.Ticker(ticker).history(period="2y")
            if len(data) < 100: continue
            
            # Prepare the data for the 'Forest'
            df = prepare_ml_data(data)
            
            # Split into Features (X) and Target (y)
            X = df[['Return', 'Range', 'Vol_Change']]
            y = df['Target']
            
            # Train the Random Forest
            # We use the last 100 days to train, then predict 'Today'
            model = RandomForestClassifier(n_estimators=50, random_state=42)
            model.fit(X.iloc[:-1], y.iloc[:-1])
            
            # Make the Prediction for Tomorrow
            prediction = model.predict(X.tail(1))[0]
            current_price = round(data['Close'].iloc[-1], 2)
            
            # ML Logic: If prediction is 1, it thinks the price will rise
            signal = "BUY" if prediction == 1 else "SELL"
            
            # --- PORTFOLIO LOGIC ---
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
                "Ticker": ticker,
                "Price": current_price,
                "Signal": signal,
                "Bought_At": buy_price,
                "P&L_%": pnl,
                "Units": 10 if (is_owned or signal == "BUY") else 0
            })
            time.sleep(1)

        except Exception as e:
            print(f"Error on {ticker}: {e}")

    portfolio.to_csv(PORTFOLIO_FILE, index=False)
    pd.DataFrame(trades_summary).to_csv("trades.csv", index=False)

if __name__ == "__main__":
    run_ml_cycle()

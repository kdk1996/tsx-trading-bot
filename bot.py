import yfinance as yf
import pandas as pd
import os

# A simple text file to act as your 'Bank' since we're keeping it simple
def run_bot():
    ticker = "SHOP.TO" # Shopify on the TSX
    data = yf.Ticker(ticker).history(period="1d")
    price = data['Close'].iloc[-1]
    
    # Save the 'Trade' to a simple text file
    with open("trades.txt", "a") as f:
        f.write(f"Date: {pd.Timestamp.now()}, Price: {price}\n")
    print(f"Bot checked {ticker}. Current price: {price}")

if __name__ == "__main__":
    run_bot()

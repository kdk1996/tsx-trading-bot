import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TSX AI Portfolio", layout="wide")

# --- 2. DATA LOADING ---
def load_data():
    try:
        df = pd.read_csv("trades.csv")
        # Ensure 'Units' and 'Bought_At' are numbers
        df['Units'] = 10 
        return df
    except:
        return None

data = load_data()

# --- 3. CALCULATE LIVE BALANCES ---
INITIAL_CASH = 100000.00
current_cash = INITIAL_CASH
total_portfolio_value = 0

if data is not None:
    # Only calculate for stocks we actually "Bought"
    owned_stocks = data[data['Bought_At'] > 0]
    money_spent = (owned_stocks['Bought_At'] * owned_stocks['Units']).sum()
    current_cash = INITIAL_CASH - money_spent
    
    # Current Value = Price * Units
    total_portfolio_value = (data['Price'] * data['Units']).sum()

# --- 4. TOP METRICS (Now Dynamic) ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Available Cash", f"${current_cash:,.2f}", "CAD")
with col2:
    total_assets = current_cash + total_portfolio_value
    profit_total = total_assets - INITIAL_CASH
    st.metric("Total Account Value", f"${total_assets:,.2f}", f"${profit_total:,.2f}")
with col3:
    st.metric("Stocks Owned", len(data[data['Bought_At'] > 0]))

st.divider()

# --- 5. UPDATED TABLE (Showing Units) ---
if data is not None:
    st.subheader("🤖 Live AI Ledger")
    
    # We add the Units column to the view
    display_df = data[['Name', 'Ticker', 'Price', 'Signal', 'Units', 'Bought_At', 'P&L_%']]
    
    def style_pnl(val):
        if val > 0: return 'color: #008148; font-weight: bold;'
        if val < 0: return 'color: #d90429; font-weight: bold;'
        return ''

    st.table(display_df.style.map(style_pnl, subset=['P&L_%']))
else:
    st.info("Run your GitHub Action to see your first trades!")

# --- 6. CHARTING (Your Alpha Vantage Key) ---
AV_API_KEY = "UG99FWTXZTMOSVFD"
# ... [rest of your charting code remains the same] ...

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import datetime

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="AI Strategy Trainer", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3 { color: #0a192f !important; }
    div[data-testid="stMetric"] { background-color: #f8f9fa; border-radius: 10px; padding: 15px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADING ---
def load_data():
    try:
        return pd.read_csv("trades.csv")
    except:
        return None

data = load_data()

# --- 3. PERFORMANCE MATH ---
INITIAL_CASH = 100000.00
if data is not None:
    # Calculate Balances
    owned = data[data['Bought_At'] > 0]
    spent = (owned['Bought_At'] * owned['Units']).sum()
    current_cash = INITIAL_CASH - spent
    port_value = (data['Price'] * data['Units']).sum()
    total_val = current_cash + port_value
    
    # Calculate Win Rate (Confidence > 50% vs Positive P&L)
    winning_trades = len(data[data['P&L_%'] > 0])
    total_trades = len(data[data['Bought_At'] > 0])
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
else:
    current_cash, total_val, win_rate = INITIAL_CASH, INITIAL_CASH, 0

# --- 4. HEADER METRICS ---
st.title("🌲 Random Forest AI Portfolio")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Available Cash", f"${current_cash:,.2f}")
with c2: st.metric("Account Value", f"${total_val:,.2f}", f"{total_val-INITIAL_CASH:,.2f}")
with c3: st.metric("AI Strategy Win Rate", f"{win_rate:.1f}%")

st.divider()

# --- 5. THE ML LEDGER ---
if data is not None:
    st.subheader("🤖 AI Confidence Ledger")
    
    def style_rows(row):
        # Color the confidence column
        styles = [''] * len(row)
        conf_idx = row.index.get_loc('Confidence_%')
        pnl_idx = row.index.get_loc('P&L_%')
        
        if row['Confidence_%'] >= 70: styles[conf_idx] = 'background-color: #fff3cd; font-weight: bold;'
        if row['P&L_%'] > 0: styles[pnl_idx] = 'color: #008148; font-weight: bold;'
        elif row['P&L_%'] < 0: styles[pnl_idx] = 'color: #d90429; font-weight: bold;'
        
        return styles

    display_df = data[['Ticker', 'Signal', 'Confidence_%', 'Price', 'Bought_At', 'P&L_%']]
    st.table(display_df.style.apply(style_rows, axis=1))
else:
    st.info("Run GitHub Action to start ML training.")

# --- 6. LIVE CHART ---
AV_API_KEY = "UG99FWTXZTMOSVFD"
selected = st.selectbox("Deep Dive Chart:", ["RY.TO", "TD.TO", "SHOP.TO", "ENB.TO", "CNQ.TO", "T.TO"])

@st.cache_data(ttl=3600)
def get_chart(ticker):
    try:
        ts = TimeSeries(key=AV_API_KEY, output_format='pandas')
        d, _ = ts.get_daily(symbol=ticker.replace(".TO", ".TRT"))
        d.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return d.head(60)
    except: return None

if selected:
    hist = get_chart(selected)
    if hist is not None:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
        fig.update_layout(template="plotly_white", height=400)
        st.plotly_chart(fig, use_container_width=True)

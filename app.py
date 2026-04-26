import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="TSX AI Bot", page_icon="📈", layout="wide")

# --- CUSTOM CSS FOR MODERN LOOK ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; }
    .stCard {
        background-color: #161b22;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title("🇨🇦 TSX AI Analysis Bot")
st.markdown("Automated Market Analysis & Paper Trading")

# --- SIDEBAR (Settings) ---
st.sidebar.header("Bot Configuration")
ticker = st.sidebar.text_input("Enter Ticker", "SHOP.TO")
fake_balance = 105420.00 # This would pull from your SQLite DB

# --- TOP ROW: KPI CARDS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Virtual Balance", f"${fake_balance:,.2f}", "+2.4%")
with col2:
    st.metric("Total Trades", "42", "6 this week")
with col3:
    st.metric("Bot Accuracy", "78%", "Adjusting...")

# --- MAIN SECTION: CHARTING ---
st.write(f"### {ticker} Market Analysis")
data = yf.download(ticker, period="3mo", interval="1d")

# Professional Candlestick Chart (Responsive)
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'],
    increasing_line_color='#00ffcc', decreasing_line_color='#ff4b4b'
)])
fig.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=20, b=20), height=400)
st.plotly_chart(fig, use_container_width=True)

# --- BOTTOM SECTION: AI RECOMMENDATION ---
st.divider()
left_col, right_col = st.columns([1, 2])

with left_col:
    st.write("#### AI Signal")
    # Simple logic for visual
    st.error("SELL SIGNAL") 
    st.info("The AI detected a 'Double Top' pattern. Recommend moving to cash.")

with right_col:
    st.write("#### Recent Ledger")
    # Sample dataframe to look like a trade history
    history = {
        "Date": ["2026-04-20", "2026-04-18", "2026-04-15"],
        "Action": ["BUY", "SELL", "BUY"],
        "Price": [102.50, 98.20, 95.00],
        "Result": ["Hold", "+$420", "Hold"]
    }
    st.table(history)

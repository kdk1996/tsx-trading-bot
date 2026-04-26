import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf

# --- 1. PAGE CONFIGURATION (Must be at the top) ---
st.set_page_config(page_title="TSX AI Investor Pro", layout="wide", page_icon="📈")

# --- 2. CUSTOM STYLE (Dark Mode Fintech Look) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #00ffcc; }
    .stTable { background-color: #161b22; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TITLE & HEADER ---
st.title("🇨🇦 TSX AI Analysis Bot")
st.caption("Automated Market Analysis & Paper Trading Dashboard")

# --- 4. DATA LOADING ---
def load_data():
    try:
        # This looks for the file created by your bot.py
        df = pd.read_csv("trades.csv")
        return df
    except FileNotFoundError:
        # This shows if the GitHub Action hasn't run successfully yet
        return None

data = load_data()

# --- 5. TOP METRICS SECTION ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Virtual Balance", "$100,000.00", "CAD")
with col2:
    if data is not None:
        buy_signals = len(data[data['Signal'] == 'BUY'])
        st.metric("Active Buy Signals", buy_signals)
    else:
        st.metric("Active Buy Signals", "0")
with col3:
    st.metric("Market", "TSX (Toronto)", "Open" if 9 <= 16 <= 16 else "Closed")

st.divider()

# --- 6. MAIN RECOMMENDATIONS TABLE ---
if data is not None:
    st.subheader("🤖 Live AI Recommendations")
    
    # Apply colors to the Signal column
    def color_signals(val):
        color = '#00ffcc' if val == 'BUY' else '#ff4b4b' if val == 'SELL' else '#ffffff'
        return f'color: {color}; font-weight: bold'

    st.table(data.style.map(color_signals, subset=['Signal']))
else:
    st.warning("⚠️ **Bot is warming up!**")
    st.info("The trade data file (trades.csv) hasn't been created yet. Please go to your GitHub Actions tab and click 'Run workflow' to start the analysis.")

# --- 7. DEEP DIVE CHARTING ---
st.divider()
st.subheader("📊 Individual Stock Deep Dive")

# List of stocks to choose from
tickers = ["SHOP.TO", "RY.TO", "ENB.TO", "CNQ.TO", "CSU.TO"]
selected = st.selectbox("Select a stock to view history:", tickers)

@st.cache_data(ttl=3600) # Remembers data for 1 hour to avoid Yahoo Finance errors
def get_chart(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d")
        return df
    except:
        return None

if selected:
    chart_data = get_chart(selected)
    if chart_data is not None and not chart_data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close'],
            increasing_line_color='#00ffcc', 
            decreasing_line_color='#ff4b4b'
        )])
        fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not load chart data. Yahoo Finance might be rate-limiting. Try again in a few minutes.")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- PAGE SETUP ---
st.set_page_config(page_title="TSX AI BOT 2026", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333; }
    h1 { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 TSX AI Investor Pro")
st.caption("Real-time Canadian Market Analysis & Paper Trading")

# --- DATA LOADING ---
@st.cache_data
def load_trades():
    try:
        return pd.read_csv("trades.csv")
    except:
        return pd.DataFrame(columns=["Date", "Name", "Ticker", "Price", "Signal"])

data = load_trades()

# --- TOP METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Portfolio Value", "$105,420.00", "+5.4%")
with col2:
    st.metric("Active Signals", len(data[data['Signal'] == 'BUY']))
with col3:
    st.metric("Market Status", "TSX: OPEN", "Toronto")

# --- MAIN ANALYSIS TABLE ---
st.write("### 🤖 Live Recommendations")
if not data.empty:
    # Color coding the signals
    def color_signal(val):
        color = '#00ffcc' if val == 'BUY' else '#ff4b4b' if val == 'SELL' else '#ffffff'
        return f'color: {color}; font-weight: bold'

    st.table(data.style.applymap(color_signal, subset=['Signal']))
else:
    st.info("Bot is warming up. Run the GitHub Action to see first trades!")

# --- INDIVIDUAL CHART ---
st.divider()
selected_ticker = st.selectbox("Deep Dive Analysis", data['Ticker'].tolist() if not data.empty else ["SHOP.TO"])
if selected_ticker:
    import yfinance as yf
    chart_data = yf.Ticker(selected_ticker).history(period="3mo")
    fig = go.Figure(data=[go.Candlestick(x=chart_data.index, open=chart_data['Open'], high=chart_data['High'], low=chart_data['Low'], close=chart_data['Close'])])
    fig.update_layout(template="plotly_dark", title=f"{selected_ticker} - 3 Month Trend")
    st.plotly_chart(fig, use_container_width=True)

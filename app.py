import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="TSX AI Total Market", layout="wide", page_icon="🇨🇦")

# --- 2. HIGH-VISIBILITY STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span { color: #0a192f !important; }
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
    }
    .stTable { background-color: #ffffff; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA LOADING & MATH ---
@st.cache_data(ttl=600)
def load_all_data():
    try:
        df = pd.read_csv("trades.csv")
        return df
    except:
        return None

data = load_all_data()

# --- 4. ACCOUNT CALCULATIONS ---
INITIAL_CASH = 100000.00
if data is not None:
    # Calculate how much cash is 'tied up' in stocks
    owned = data[data['Bought_At'] > 0]
    cash_spent = (owned['Bought_At'] * owned['Units']).sum()
    current_cash = INITIAL_CASH - cash_spent
    portfolio_value = (data['Price'] * data['Units']).sum()
    total_value = current_cash + portfolio_value
    net_profit = total_value - INITIAL_CASH
else:
    current_cash, total_value, net_profit = INITIAL_CASH, INITIAL_CASH, 0

# --- 5. TOP METRICS ---
st.title("📊 TSX AI Total Market Trainer")
c1, c2, c3 = st.columns(3)
with c1: st.metric("Available Cash", f"${current_cash:,.2f}")
with c2: st.metric("Total Account Value", f"${total_value:,.2f}", f"${net_profit:,.2f}")
with c3: st.metric("Market Exposure", "Elite 25 Index", "2026 Active")

st.divider()

# --- 6. THE MASTER LEDGER ---
if data is not None:
    st.subheader("🤖 Strategy Ledger: All Watchlist Stocks")
    
    def color_pnl(val):
        if val > 0: return 'color: #008148; font-weight: bold;'
        if val < 0: return 'color: #d90429; font-weight: bold;'
        return 'color: #0a192f;'

    display_cols = ['Name', 'Ticker', 'Price', 'Signal', 'Bought_At', 'P&L_%']
    
    try:
        st.table(data[display_cols].style.map(color_pnl, subset=['P&L_%']))
    except:
        st.table(data[display_cols].style.applymap(color_pnl, subset=['P&L_%']))
else:
    st.info("🔄 Bot is initializing. Please run the GitHub Action to populate this table.")

# --- 7. DEEP DIVE CHARTING ---
st.divider()
st.subheader("🔍 Individual Trend Analysis")

AV_API_KEY = "UG99FWTXZTMOSVFD"
tickers = ["RY.TO", "TD.TO", "BNS.TO", "BMO.TO", "CM.TO", "BN.TO", "ENB.TO", "CNQ.TO", "SU.TO", "TRP.TO", "CCO.TO", "SHOP.TO", "CSU.TO", "DSG.TO", "CNR.TO", "CP.TO", "ATD.TO", "AEM.TO", "ABX.TO", "WPM.TO", "T.TO", "BCE.TO", "FTS.TO"]

selected = st.selectbox("Select a ticker to view 2026 performance:", tickers)

@st.cache_data(ttl=3600)
def get_av_data(ticker):
    try:
        ts = TimeSeries(key=AV_API_KEY, output_format='pandas')
        chart_data, _ = ts.get_daily(symbol=ticker.replace(".TO", ".TRT"))
        chart_data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return chart_data.head(60)
    except:
        return None

if selected:
    hist = get_av_data(selected)
    if hist is not None:
        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'], increasing_line_color='#008148', decreasing_line_color='#d90429')])
        fig.update_layout(template="plotly_white", height=450, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("API Limit reached (25 per day). The table above is still active!")

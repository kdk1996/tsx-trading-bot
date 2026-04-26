import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="TSX AI Investor Pro", layout="wide", page_icon="📈")

# --- 2. HIGH-VISIBILITY LIGHT THEME ---
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    h1, h2, h3, p, span, label { color: #0a192f !important; }
    
    /* Metric Card Styling */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Table Visibility */
    .stTable { 
        background-color: #ffffff; 
        border: 1px solid #dee2e6;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. TITLE ---
st.title("🇨🇦 TSX AI Analysis Bot")
st.caption("Strategic Investment Analysis | 2026 Edition")

# --- 4. DATA LOADING (From GitHub Action) ---
def load_data():
    try:
        df = pd.read_csv("trades.csv")
        return df
    except:
        return None

data = load_data()

# --- 5. TOP METRICS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Virtual Portfolio", "$100,000.00", "CAD")
with col2:
    status = "READY" if data is not None else "WAITING"
    st.metric("System Status", status)
with col3:
    st.metric("Exchange", "TSX", "Toronto")

st.divider()

# --- 6. RECOMMENDATIONS TABLE ---
if data is not None:
    st.subheader("🤖 Live AI Recommendations")
    
    def color_signals(val):
        if val == 'BUY': return 'color: #008148; font-weight: bold;' # Dark Green
        if val == 'SELL': return 'color: #d90429; font-weight: bold;' # Bright Red
        return 'color: #2b2d42;'

    # Universal Pandas support for styling
    try:
        styled_table = data.style.map(color_signals, subset=['Signal'])
    except AttributeError:
        styled_table = data.style.applymap(color_signals, subset=['Signal'])
        
    st.table(styled_table)
else:
    st.warning("⚠️ **Bot is warming up!**")
    st.info("The trade data (trades.csv) isn't ready. Go to your GitHub Actions tab and click 'Run workflow'.")

# --- 7. ALPHA VANTAGE CHARTING (Rate-Limit Proof) ---
st.divider()
st.subheader("📊 Individual Stock Deep Dive")

AV_API_KEY = "UG99FWTXZTMOSVFD" 

@st.cache_data(ttl=3600)
def get_av_chart(ticker):
    try:
        # Convert SHOP.TO to SHOP.TRT for Alpha Vantage
        av_ticker = ticker.replace(".TO", ".TRT")
        ts = TimeSeries(key=AV_API_KEY, output_format='pandas')
        # Fetching Daily data (approx 4 months)
        data_ts, meta_data = ts.get_daily(symbol=av_ticker)
        
        # Alpha Vantage uses numbered column names, we must rename them
        data_ts.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        return data_ts.head(60) # Last 60 trading days
    except Exception as e:
        return None

tickers = ["SHOP.TO", "RY.TO", "ENB.TO", "CNQ.TO", "CSU.TO"]
selected = st.selectbox("Select a stock for trend analysis:", tickers)

if selected:
    with st.spinner('Fetching high-precision data...'):
        chart_data = get_av_chart(selected)
    
    if chart_data is not None and not chart_data.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close'],
            increasing_line_color='#008148', 
            decreasing_line_color='#d90429'
        )])
        fig.update_layout(
            template="plotly_white", # Matches our light theme
            height=450, 
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Data source currently unavailable. This can happen if the API key is used too many times in one minute.")

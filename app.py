import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. DESIGN & LAYOUT ---
st.set_page_config(page_title="Nexus Terminal v2", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0d11; color: #e0e0e0; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Courier New', monospace; }
    .status-card { border: 1px solid #1f2937; padding: 20px; border-radius: 12px; background: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA HANDLING ---
def load_data():
    trades = pd.read_csv("trades.csv") if os.path.exists("trades.csv") else pd.DataFrame()
    portfolio = pd.read_csv("portfolio.csv") if os.path.exists("portfolio.csv") else pd.DataFrame()
    return trades, portfolio

trades, portfolio = load_data()

# --- 3. TOP BAR: FINANCIAL HUD ---
st.title("🏛️ Nexus Market Terminal")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Equity", "$102,400", "+2.4%")
m2.metric("Cash Reserve", "$85,000", "-$15k")
m3.metric("AI Coverage", f"{len(trades)} Stocks")
m4.metric("Market Sentiment", "Bullish", "72%")

st.divider()

# --- 4. THE INTERACTIVE GRID (The "All Stocks" View) ---
st.subheader("📡 Live AI Strategy Feed (All Levels)")

if not trades.empty:
    # We create a 4-column grid for the stock cards
    cols = st.columns(4)
    for i, row in trades.iterrows():
        with cols[i % 4]:
            # Color logic based on Signal, not just confidence
            border_color = "#00ff88" if row['Signal'] == "BUY" else "#ff4b4b" if row['Signal'] == "SELL" else "#6b7280"
            
            st.markdown(f"""
            <div style="border-left: 5px solid {border_color}; padding: 15px; background: #1f2937; border-radius: 8px; margin-bottom: 10px;">
                <h3 style="margin:0;">{row['Ticker']}</h3>
                <p style="margin:0; font-size: 0.8em; color: #9ca3af;">Confidence: {row['Confidence_%']}%</p>
                <h4 style="color: {border_color}; margin-top: 5px;">{row['Signal']}</h4>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("No live trade data found. Trigger the GitHub Action to populate the grid.")

# --- 5. PORTFOLIO VISUALIZER (The Treemap) ---
st.divider()
st.subheader("📂 Your Virtual Assets")

col_left, col_right = st.columns([2, 1])

with col_left:
    if not portfolio.empty:
        # This is the "Heatmap" you asked for
        fig = px.treemap(portfolio, 
                         path=['Ticker'], 
                         values='Units', 
                         color='Buy_Price',
                         color_continuous_scale='RdYlGn',
                         title="Portfolio Allocation")
        fig.update_layout(margin=dict(t=30, l=10, r=10, b=10), paper_bgcolor="#111827", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No shares owned yet.")

with col_right:
    st.markdown("### ✍️ Manual Order")
    with st.form("manual_trade"):
        t_input = st.text_input("Ticker", placeholder="AAPL")
        q_input = st.number_input("Quantity", min_value=1, value=10)
        action = st.selectbox("Action", ["Buy", "Sell"])
        if st.form_submit_button("Submit Order"):
            st.success(f"Order for {q_input} units of {t_input} queued!")

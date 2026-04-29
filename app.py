import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. THEME & NEON STYLING ---
st.set_page_config(page_title="Nexus AI v2", layout="wide")

st.markdown("""
    <style>
    /* Midnight background with neon accents */
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    /* Neon Cyan Metrics */
    [data-testid="stMetricValue"] { 
        color: #00f2ff !important; 
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.3);
    }
    
    /* Terminal-style Cards */
    .terminal-card {
        border: 1px solid #1a1e26;
        background: linear-gradient(145deg, #0d1117, #161b22);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 5px 5px 15px #05070a, -5px -5px 15px #0d1117;
    }
    
    /* Clean, professional tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        color: #8b949e;
    }
    .stTabs [aria-selected="true"] { color: #ffd700 !important; border-bottom-color: #ffd700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA UTILITIES ---
def load_data():
    trades = pd.read_csv("trades.csv") if os.path.exists("trades.csv") else pd.DataFrame()
    port = pd.read_csv("portfolio.csv") if os.path.exists("portfolio.csv") else pd.DataFrame()
    return trades, port

trades, portfolio = load_data()

# --- 3. THE HUD (Top Metrics) ---
st.title("🏛️ NEXUS TERMINAL")
c1, c2, c3, c4 = st.columns(4)

# Dynamic Math
cash = 100000.00 # Placeholder for your virtual bank
invested = (portfolio['Buy_Price'] * portfolio['Units']).sum() if not portfolio.empty else 0

c1.metric("TOTAL EQUITY", f"${(cash + invested):,.0f}", "+2.4%")
c2.metric("LIQUID CASH", f"${cash:,.0f}")
c3.metric("MARKET EXPOSURE", f"{len(portfolio)} Positions")
c4.metric("AI CONVICTION", "BULLISH" if invested > 0 else "NEUTRAL")

st.divider()

# --- 4. MAIN INTERACTIVE ENGINE ---
tab1, tab2 = st.tabs(["⚡ AI STRATEGY FEED", "📁 PORTFOLIO ASSETS"])

with tab1:
    st.subheader("Real-Time Signal Matrix")
    if not trades.empty:
        # Create a density grid of 5 columns
        grid = st.columns(5)
        for i, row in trades.iterrows():
            with grid[i % 5]:
                # Signal Color logic
                accent = "#00ff88" if row['Signal'] == "BUY" else "#ff4b4b" if row['Signal'] == "SELL" else "#8b949e"
                st.markdown(f"""
                <div class="terminal-card" style="border-top: 3px solid {accent};">
                    <p style="color: #8b949e; font-size: 0.7em; margin:0;">{row['Ticker']}</p>
                    <h2 style="margin: 5px 0;">{row['Signal']}</h2>
                    <p style="color: {accent}; font-size: 0.8em; margin:0;">Conf: {row['Confidence_%']}%</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No active signals. Run the AI engine via GitHub.")

with tab2:
    if not portfolio.empty:
        col_viz, col_data = st.columns([2, 1])
        with col_viz:
            # Modern Treemap for visual allocation
            fig = px.treemap(portfolio, path=['Ticker'], values='Units',
                             color_discrete_sequence=['#ffd700'], # Gold theme
                             hover_data=['Buy_Price'])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        with col_data:
            st.markdown("### Active Holdings")
            st.dataframe(portfolio, use_container_width=True, hide_index=True)
    else:
        st.warning("No shares owned. Use the manual entry to invest your virtual money.")

# --- 5. THE MANUAL TRADING FLOOR ---
st.divider()
with st.expander("🛠️ MANUAL ORDER ENTRY"):
    c_tick, c_qty, c_btn = st.columns([2, 1, 1])
    ticker_input = c_tick.text_input("Enter Ticker", placeholder="e.g., AAPL")
    qty_input = c_qty.number_input("Shares", min_value=1, value=10)
    if c_btn.button("EXECUTE ORDER", type="primary"):
        st.balloons()
        st.success(f"Order for {qty_input} {ticker_input} sent to virtual ledger!")

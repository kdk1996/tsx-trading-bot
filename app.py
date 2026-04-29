import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. NEON TERMINAL STYLING ---
st.set_page_config(page_title="Nexus AI Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    /* Neon Blue Metrics */
    [data-testid="stMetricValue"] { 
        color: #00f2ff !important; 
        font-family: 'JetBrains Mono', monospace;
        text-shadow: 0 0 8px rgba(0, 242, 255, 0.4);
    }
    
    /* Terminal Signal Cards */
    .signal-card {
        border: 1px solid #1a1e26;
        background: #0d1117;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    /* Custom Gold Tabs */
    .stTabs [aria-selected="true"] { color: #ffd700 !important; border-bottom-color: #ffd700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA CORE ---
def load_nexus_data():
    trades = pd.read_csv("trades.csv") if os.path.exists("trades.csv") else pd.DataFrame()
    port = pd.read_csv("portfolio.csv") if os.path.exists("portfolio.csv") else pd.DataFrame()
    hist = pd.read_csv("history.csv") if os.path.exists("history.csv") else pd.DataFrame()
    return trades, port, hist

trades, portfolio, history = load_nexus_data()

# --- 3. THE HUD (Top Bar) ---
st.title("🏛️ NEXUS MARKET TERMINAL")
c1, c2, c3, c4 = st.columns(4)

initial_cash = 100000.00
# Calculate current holdings value
current_val = (portfolio['Buy_Price'] * portfolio['Units']).sum() if not portfolio.empty else 0
# Calculate total profit from history
total_profit = history['Profit_$'].sum() if not history.empty else 0

c1.metric("TOTAL EQUITY", f"${(initial_cash + total_profit + current_val):,.2f}")
c2.metric("LIFETIME PROFIT", f"${total_profit:,.2f}", f"{((total_profit/initial_cash)*100):.2f}%")
c3.metric("ACTIVE POSITIONS", len(portfolio))
c4.metric("SYSTEM STATUS", "AUTO-TRADING", "Online")

st.divider()

# --- 4. MAIN ENGINE TABS ---
tab1, tab2, tab3 = st.tabs(["⚡ AI TREND ANALYZER", "📁 PORTFOLIO ASSETS", "📜 TRADE LOGS"])

with tab1:
    st.subheader("Market Scan & Predictive Signals")
    if not trades.empty:
        grid = st.columns(4)
        for i, row in trades.iterrows():
            with grid[i % 4]:
                accent = "#00ff88" if row['Signal'] == "BUY" else "#ff4b4b" if row['Signal'] == "SELL" else "#8b949e"
                owned_tag = "⭐" if not portfolio.empty and row['Ticker'] in portfolio['Ticker'].values else ""
                
                st.markdown(f"""
                <div class="signal-card" style="border-top: 3px solid {accent};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #8b949e; font-size: 0.8em;">{row['Ticker']}</span>
                        <span>{owned_tag}</span>
                    </div>
                    <h2 style="margin: 5px 0; color: white;">{row['Signal']}</h2>
                    <p style="color: {accent}; font-size: 0.9em; margin:0;">AI Confidence: {row['Confidence_%']}%</p>
                    <p style="font-size: 0.8em; margin-top: 5px;">Mkt Price: ${row['Price']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No trend data available. Waiting for next AI cycle.")

with tab2:
    if not portfolio.empty:
        v_col, d_col = st.columns([2, 1])
        with v_col:
            fig = px.treemap(portfolio, path=['Ticker'], values='Units',
                             color_discrete_sequence=['#ffd700']) # Gold Assets
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
        with d_col:
            st.markdown("### Asset Inventory")
            st.dataframe(portfolio, use_container_width=True, hide_index=True)
    else:
        st.warning("No active investments found in the ledger.")

with tab3:
    st.subheader("Closed Positions Journal")
    if not history.empty:
        st.dataframe(history.sort_values(by='Profit_$', ascending=False), use_container_width=True)
    else:
        st.info("The history ledger is empty. It will populate when the AI or you trigger a SELL.")

# --- 5. THE MANUAL TRADING FLOOR ---
st.divider()
with st.expander("🛠️ MANUAL ORDER OVERRIDE"):
    st.write("Invest virtual money in shares of your choice.")
    m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
    man_ticker = m_col1.text_input("Ticker Symbol", placeholder="e.g., TSLA")
    man_qty = m_col2.number_input("Shares", min_value=1, value=10)
    
    if m_col3.button("EXECUTE BUY", type="primary"):
        if man_ticker:
            st.success(f"Order Executed: {man_qty} shares of {man_ticker.upper()}. Check Portfolio tab.")
            st.balloons()
        else:
            st.error("Please enter a ticker symbol.")

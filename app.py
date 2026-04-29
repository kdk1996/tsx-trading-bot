import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. CLEAN LIGHT THEME STYLING ---
st.set_page_config(page_title="Nexus Analytics", layout="wide")

st.markdown("""
    <style>
    /* Clean white background with dark text */
    .stApp { background-color: #FFFFFF; color: #1e293b; }
    
    /* Deep Navy Metrics for readability */
    [data-testid="stMetricValue"] { 
        color: #0f172a !important; 
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Professional Grey Cards */
    .signal-card {
        border: 1px solid #e2e8f0;
        background: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Tab Styling: Navy for active, Grey for inactive */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [aria-selected="true"] { color: #1d4ed8 !important; border-bottom-color: #1d4ed8 !important; }
    
    /* Headers */
    h1, h2, h3 { color: #0f172a !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADERS ---
def load_nexus_data():
    trades = pd.read_csv("trades.csv") if os.path.exists("trades.csv") else pd.DataFrame()
    port = pd.read_csv("portfolio.csv") if os.path.exists("portfolio.csv") else pd.DataFrame()
    hist = pd.read_csv("history.csv") if os.path.exists("history.csv") else pd.DataFrame()
    return trades, port, hist

trades, portfolio, history = load_nexus_data()

# --- 3. TOP FINANCIAL HUD ---
st.title("📊 Nexus Trading Intelligence")
c1, c2, c3, c4 = st.columns(4)

initial_cash = 100000.00
current_val = (portfolio['Buy_Price'] * portfolio['Units']).sum() if not portfolio.empty else 0
total_profit = history['Profit_$'].sum() if not history.empty else 0

c1.metric("TOTAL EQUITY", f"${(initial_cash + total_profit + current_val):,.2f}")
c2.metric("LIFETIME PROFIT", f"${total_profit:,.2f}", f"{((total_profit/initial_cash)*100):.2f}%")
c3.metric("ACTIVE POSITIONS", len(portfolio))
c4.metric("SYSTEM STATUS", "ONLINE", "Auto-Mode")

st.divider()

# --- 4. MAIN INTERFACE ---
tab1, tab2, tab3 = st.tabs(["🎯 AI Signals", "📂 My Portfolio", "📜 History"])

with tab1:
    st.subheader("Market Scan & AI Logic")
    if not trades.empty:
        grid = st.columns(4)
        for i, row in trades.iterrows():
            with grid[i % 4]:
                # Stronger, more readable colors
                accent = "#059669" if row['Signal'] == "BUY" else "#dc2626" if row['Signal'] == "SELL" else "#64748b"
                owned_tag = "🔵 ACTIVE" if not portfolio.empty and row['Ticker'] in portfolio['Ticker'].values else ""
                
                st.markdown(f"""
                <div class="signal-card" style="border-left: 5px solid {accent};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #64748b; font-weight: bold;">{row['Ticker']}</span>
                        <span style="color: #1d4ed8; font-size: 0.7em; font-weight: bold;">{owned_tag}</span>
                    </div>
                    <h2 style="margin: 5px 0; color: #0f172a;">{row['Signal']}</h2>
                    <p style="color: {accent}; font-weight: bold; margin:0;">Confidence: {row['Confidence_%']}%</p>
                    <p style="font-size: 0.9em; margin-top: 5px; color: #334155;">Price: ${row['Price']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Waiting for trend data...")

with tab2:
    if not portfolio.empty:
        v_col, d_col = st.columns([2, 1])
        with v_col:
            # High-contrast color scale
            fig = px.treemap(portfolio, path=['Ticker'], values='Units',
                             color='Buy_Price', color_continuous_scale='Blues') 
            fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
        with d_col:
            st.write("### Active Inventory")
            st.dataframe(portfolio, use_container_width=True, hide_index=True)
    else:
        st.warning("No active investments to display.")

with tab3:
    st.subheader("Closed Trade Journal")
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)

# --- 5. INTERACTIVE ORDER OVERRIDE ---
st.divider()
with st.expander("📝 MANUAL ORDER ENTRY"):
    m_col1, m_col2, m_col3 = st.columns([2, 1, 1])
    man_ticker = m_col1.text_input("Ticker Symbol", placeholder="e.g., RY.TO")
    man_qty = m_col2.number_input("Shares", min_value=1, value=10)
    if m_col3.button("EXECUTE BUY", type="primary"):
        st.success(f"Virtual order for {man_qty} shares of {man_ticker.upper()} recorded.")

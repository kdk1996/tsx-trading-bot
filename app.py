import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. DESIGN & HUD ---
st.set_page_config(page_title="Nexus Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0d11; color: #e0e0e0; }
    .status-card { border: 1px solid #3d3f4b; padding: 20px; border-radius: 12px; background: #111827; margin-bottom: 20px; }
    [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOADERS ---
def load_all_data():
    # Load AI Signals
    trades_df = pd.read_csv("trades.csv") if os.path.exists("trades.csv") else pd.DataFrame()
    # Load Current Holdings
    portfolio_df = pd.read_csv("portfolio.csv") if os.path.exists("portfolio.csv") else pd.DataFrame()
    # Load History
    history_df = pd.read_csv("history.csv") if os.path.exists("history.csv") else pd.DataFrame()
    return trades_df, portfolio_df, history_df

trades, portfolio, history = load_all_data()

# --- 3. TOP FINANCIAL HUD ---
st.title("🏛️ Nexus Market Terminal")
m1, m2, m3, m4 = st.columns(4)

# Dynamic metrics
total_invested = (portfolio['Buy_Price'] * portfolio['Units']).sum() if not portfolio.empty else 0
account_val = 100000 + (portfolio['Units'] * 10).sum() # Simplified for display

m1.metric("Account Value", f"${account_val:,.2f}")
m2.metric("Total Invested", f"${total_invested:,.2f}")
m3.metric("Active Positions", len(portfolio))
m4.metric("AI Confidence Avg", f"{trades['Confidence_%'].mean():.1f}%" if not trades.empty else "0%")

st.divider()

# --- 4. THE TWO-WAY VIEW ---
tab1, tab2, tab3 = st.tabs(["🎯 Live Market & AI Signals", "📂 My Active Portfolio", "📜 History"])

with tab1:
    st.subheader("📡 All Tracked Stocks & AI Predictions")
    if not trades.empty:
        # Show a grid of all stocks being watched
        cols = st.columns(4)
        for i, row in trades.iterrows():
            with cols[i % 4]:
                color = "#00ff88" if row['Signal'] == "BUY" else "#ff4b4b" if row['Signal'] == "SELL" else "#9ca3af"
                is_invested = "💰 OWNED" if not portfolio.empty and row['Ticker'] in portfolio['Ticker'].values else ""
                
                st.markdown(f"""
                <div style="border-top: 4px solid {color}; padding: 15px; background: #1f2937; border-radius: 8px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between;">
                        <h3 style="margin:0;">{row['Ticker']}</h3>
                        <span style="color: #ffd700; font-size: 0.8em; font-weight: bold;">{is_invested}</span>
                    </div>
                    <p style="margin:0; font-size: 0.8em; color: #9ca3af;">AI Confidence: {row['Confidence_%']}%</p>
                    <h2 style="color: {color}; margin: 10px 0;">{row['Signal']}</h2>
                    <p style="margin:0; font-size: 0.9em;">Price: ${row['Price']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Run the GitHub Action to see AI signals.")

with tab2:
    st.subheader("📂 Your Active Investments")
    if not portfolio.empty:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            # Treemap shows size of investment
            fig = px.treemap(portfolio, path=['Ticker'], values='Units', 
                             color='Buy_Price', color_continuous_scale='RdYlGn',
                             title="Asset Allocation (Size = Units Owned)")
            fig.update_layout(paper_bgcolor="#111827", font_color="white", margin=dict(t=30, l=0, r=0, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_right:
            st.write("### Detailed List")
            st.dataframe(portfolio, use_container_width=True, hide_index=True)
    else:
        st.warning("You currently have no active investments.")

with tab3:
    st.subheader("📜 Historical Trade Journal")
    if not history.empty:
        st.table(history)
    else:
        st.info("No trades have been closed yet.")

# --- 5. INTERACTIVE ORDER ENTRY ---
st.divider()
with st.expander("🚀 Manual Trade Entry"):
    with st.form("order_form"):
        st.write("Invest in shares you like with your virtual $100k.")
        c1, c2, c3 = st.columns(3)
        t_in = c1.text_input("Ticker Symbol", placeholder="e.g., AAPL")
        q_in = c2.number_input("Units to Buy", min_value=1, value=10)
        submit = st.form_submit_button("Execute Virtual Order")
        
        if submit:
            st.success(f"Virtual order for {q_in} shares of {t_in} submitted to the ledger!")

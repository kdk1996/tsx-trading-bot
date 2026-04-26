# --- RATE-LIMIT PROOF CHARTING ---
st.divider()
selected_ticker = st.selectbox("Deep Dive Analysis", data['Ticker'].tolist() if not data.empty else ["SHOP.TO"])

@st.cache_data(ttl=3600) # This tells the app to "remember" the data for 1 hour
def get_chart_data(symbol):
    try:
        # We fetch a smaller amount of data to stay under the radar
        ticker_obj = yf.Ticker(symbol)
        return ticker_obj.history(period="1mo") 
    except Exception as e:
        st.error("Yahoo Finance is busy. Please try again in 5 minutes.")
        return None

if selected_ticker:
    chart_data = get_chart_data(selected_ticker)
    if chart_data is not None:
        fig = go.Figure(data=[go.Candlestick(
            x=chart_data.index,
            open=chart_data['Open'],
            high=chart_data['High'],
            low=chart_data['Low'],
            close=chart_data['Close']
        )])
        fig.update_layout(template="plotly_dark", title=f"{selected_ticker} Trend")
        st.plotly_chart(fig, use_container_width=True)

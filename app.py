
import streamlit as st
from backend.runner import run_all_scripts, run_weekly_setup
from backend.charts import plot_stock_chart
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Swing Analyst", layout="wide")

st.title("📊 Swing Analyst Dashboard")
st.sidebar.header("Navigation")
page = st.sidebar.selectbox("Go to", ["Home", "Delivery Analysis", "Bullish Stocks","Stock Charts","Sector Rotation"])

DATA_DIR = "data"

# --- HOME PAGE ---
if page == "Home":
    st.header("⚙️ System Panel")
    st.caption("Run weekly setup only after friday market close, and day pipeline can be run daily after market close.")

    # --- Day Pipeline ---
    if st.button("Run Day Pipeline"):
        with st.spinner("Running all scripts for daily setup..."):
            run_all_scripts()
        st.success("✅ Day Pipeline completed successfully!")

    # --- Weekly Pipeline ---
    if st.button("Run Weekly Setup"):
        with st.spinner("Running weekly setup..."):
            run_weekly_setup()
        st.success("✅ Weekly setup completed successfully!")


# --- DELIVERY ANALYSIS PAGE ---
elif page == "Delivery Analysis":
    st.caption("Showing latest 50 records from delivery_highest and delivery_spike databases.")
    
    st.header("📈 Delivery Highest Records")
    try:
        conn = sqlite3.connect(os.path.join(DATA_DIR, "delivery_highest.db"))
        df = pd.read_sql_query("SELECT * FROM delivery_highest ORDER BY SIGNAL_DATE DESC LIMIT 50", conn)
        conn.close()
        st.dataframe(df)
    except Exception as e:
        st.warning(f"Could not load delivery_highest.db: {e}")

    st.header("⚡ Delivery Spike Records")
    try:
        conn = sqlite3.connect(os.path.join(DATA_DIR, "delivery_spike.db"))
        df = pd.read_sql_query("SELECT * FROM delivery_spike ORDER BY SIGNAL_DATE DESC LIMIT 50", conn)
        conn.close()
        st.dataframe(df.sort_values(by="SIGNAL_DATE", ascending=False))
    except Exception as e:
        st.warning(f"Could not load delivery_spike.db: {e}")

# --- BULLISH STOCKS PAGE ---
elif page == "Bullish Stocks":
    st.caption("Showing stocks which have closed positive in delivery_highest and delivery_spike databases.")

    st.header("📗 Delivery Highest Bullish Stocks")
    try:
        conn = sqlite3.connect(os.path.join(DATA_DIR, "bullish_stocks.db"))
        df = pd.read_sql_query("""
            SELECT * FROM bullish_stocks 
            WHERE SIGNAL_DATE = (SELECT max(SIGNAL_DATE) FROM bullish_stocks)
        """, conn)
        conn.close()
        st.dataframe(df)
    except Exception as e:
        st.warning(f"Could not load bullish_stocks.db: {e}")

    st.header("📘 Delivery Spike Bullish Stocks")
    try:
        conn = sqlite3.connect(os.path.join(DATA_DIR, "del_bullish_stocks.db"))
        df = pd.read_sql_query("""
            SELECT * FROM del_bullish_stocks 
            WHERE SIGNAL_DATE = (SELECT max(SIGNAL_DATE) FROM del_bullish_stocks)
        """, conn)
        conn.close()
        st.dataframe(df)
    except Exception as e:
        st.warning(f"Could not load del_bullish_stocks.db: {e}")

# --- STOCK CHARTS PAGE ---
elif page == "Stock Charts":
    st.header("📉 Stock Price Charts")
    symbol = st.text_input("Enter symbol:").upper()
    if symbol:
        fig = plot_stock_chart(symbol)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Sector Rotation":
    st.header("Sector Rotation")
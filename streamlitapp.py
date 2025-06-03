import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# --- DB Configuration ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432"),
    "name": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

# Initialize database connection
@st.cache_resource
def init_connection():
    try:
        return create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['name']}"
        )
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        return None

# Cache data loading
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_db(asset_type, ticker, start, end):
    table_map = {
        "stock": "stock_data",
        "etf": "etf_data",
        "crypto": "crypto_data"
    }
    table = table_map.get(asset_type)
    if not table:
        return pd.DataFrame()

    try:
        engine = init_connection()
        if not engine:
            return pd.DataFrame()

        query = f"""
            SELECT date, open, high, low, close, volume 
            FROM {table}
            WHERE ticker = %s AND date BETWEEN %s AND %s
            ORDER BY date
        """
        df = pd.read_sql(query, engine, params=[ticker, start, end])
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def calculate_metrics(df):
    if df.empty:
        return {}
    
    latest_price = df['close'].iloc[-1]
    daily_returns = df['close'].pct_change()
    
    metrics = {
        'Latest Price': f"${latest_price:.2f}",
        'Daily Return': f"{daily_returns.iloc[-1]:.2%}",
        'Volatility (30d)': f"{daily_returns.rolling(30).std().iloc[-1]:.2%}",
        'Average Volume': f"{df['volume'].mean():,.0f}",
        'Highest Price': f"${df['high'].max():.2f}",
        'Lowest Price': f"${df['low'].min():.2f}"
    }
    return metrics

def main():
    st.set_page_config(
        page_title="Investing Insights Dashboard",
        page_icon="📈",
        layout="wide"
    )

    # --- Sidebar ---
    st.sidebar.title("📊 Investing Insights")
    
    asset_type = st.sidebar.selectbox(
        "Select Asset Type",
        ["stock", "etf", "crypto"],
        help="Choose the type of asset you want to analyze"
    )
    
    ticker = st.sidebar.text_input(
        "Enter Ticker",
        "AAPL",
        help="Enter the ticker symbol (e.g., AAPL, SPY, BTC-USD)"
    ).upper()

    # Date range selector with reasonable defaults
    default_end = datetime.now()
    default_start = default_end - timedelta(days=365)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", default_start)
    with col2:
        end_date = st.date_input("End Date", default_end)

    # --- Main Content ---
    st.title(f"💹 {ticker} Analysis")
    
    # Load and validate data
    df = load_data_from_db(asset_type, ticker, start_date, end_date)
    
    if df.empty:
        st.warning("No data found. Please check if the ticker is correct and data is available for the selected period.")
        return

    # Create two columns for metrics and charts
    metrics_col, chart_col = st.columns([1, 3])
    
    with metrics_col:
        st.subheader("📊 Key Metrics")
        metrics = calculate_metrics(df)
        for metric, value in metrics.items():
            st.metric(metric, value)
    
    with chart_col:
        # Candlestick Chart
        st.subheader("📈 Price Action")
        fig = go.Figure(data=[go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="OHLC"
        )])
        
        # Add moving averages
        ma20 = df['close'].rolling(window=20).mean()
        ma50 = df['close'].rolling(window=50).mean()
        
        fig.add_trace(go.Scatter(x=df['date'], y=ma20, name='20 MA', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df['date'], y=ma50, name='50 MA', line=dict(color='blue')))
        
        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    # Volume Chart
    st.subheader("📊 Volume Analysis")
    volume_fig = go.Figure(data=[
        go.Bar(
            x=df['date'],
            y=df['volume'],
            name='Volume'
        )
    ])
    volume_fig.update_layout(
        template='plotly_dark',
        height=300
    )
    st.plotly_chart(volume_fig, use_container_width=True)

    # Additional Analysis
    st.subheader("📈 Performance Statistics")
    with st.expander("View Detailed Statistics"):
        st.dataframe(df.describe().round(2))

if __name__ == "__main__":
    main()

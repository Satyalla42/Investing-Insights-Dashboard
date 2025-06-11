from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create necessary directories if they don't exist
os.makedirs('templates', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

# Load environment variables
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    """Get database connection"""
    try:
        DB_CONFIG = {
            "host": "investing-insights-db1.cpmkiuwmc3bi.eu-north-1.rds.amazonaws.com",
            "port": 5432,
            "database": "postgres",
            "user": "postgres",
            "password": 
            "sslmode": "require"
        }
        
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        logger.info(f"Successfully connected to database at {DB_CONFIG['host']}")
        return engine
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return None

def get_available_tickers(asset_type):
    """Get list of available tickers for the given asset type"""
    table_map = {
        "stock": "stock_data",
        "etf": "etf_data",
        "crypto": "crypto_data"
    }
    table = table_map.get(asset_type)
    
    try:
        engine = get_db_connection()
        query = f"SELECT DISTINCT ticker FROM {table} ORDER BY ticker"
        logger.info(f"Fetching tickers from {table}")
        df = pd.read_sql(query, engine)
        logger.info(f"Found {len(df)} tickers in {table}")
        return df['ticker'].tolist()
    except Exception as e:
        logger.error(f"Error getting tickers: {str(e)}")
        return []

def validate_ticker(ticker, asset_type):
    """Validate if ticker exists in the database"""
    available_tickers = get_available_tickers(asset_type)
    return ticker in available_tickers

def load_data_from_db(asset_type, ticker, start_date, end_date):
    table_map = {
        "stock": "stock_data",
        "etf": "etf_data",
        "crypto": "crypto_data"
    }
    table = table_map.get(asset_type)
    if not table:
        logger.error(f"Invalid asset type: {asset_type}")
        return pd.DataFrame()

    try:
        engine = get_db_connection()
        if not engine:
            return pd.DataFrame()

        # Get the data using the simpler query that works
        query = f"""
            SELECT date, open, high, low, close, volume 
            FROM {table}
            WHERE ticker = %(ticker)s AND date BETWEEN %(start_date)s AND %(end_date)s
            ORDER BY date
        """
        
        params = {
            "ticker": ticker,
            "start_date": start_date,
            "end_date": end_date
        }
        logger.info(f"Executing query with parameters: {params}")
        df = pd.read_sql(query, engine, params=params)
        
        if df.empty:
            logger.warning(f"No data found for {ticker} between {start_date} and {end_date}")
            return df
            
        # Remove any remaining invalid data
        df = df.dropna()
        
        # Log data statistics
        logger.info(f"Successfully loaded {len(df)} rows for {ticker}")
        logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
        logger.info(f"Price range: ${df['low'].min():.2f} - ${df['high'].max():.2f}")
        logger.info(f"Number of up days: {len(df[df['close'] > df['open']])}")
        logger.info(f"Number of down days: {len(df[df['close'] < df['open']])}")
        
        return df
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return pd.DataFrame()

def calculate_metrics(df):
    if df.empty:
        return {}
    
    latest_price = df['close'].iloc[-1]
    daily_returns = df['close'].pct_change()
    
    return {
        'Latest Price': f"${latest_price:.2f}",
        'Daily Return': f"{daily_returns.iloc[-1]:.2%}",
        'Volatility (30d)': f"{daily_returns.rolling(30).std().iloc[-1]:.2%}",
        'Average Volume': f"{df['volume'].mean():,.0f}",
        'Highest Price': f"${df['high'].max():.2f}",
        'Lowest Price': f"${df['low'].min():.2f}"
    }

def create_candlestick_chart(df):
    if df.empty:
        return None

    # Create candlestick chart
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
    
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=ma20, 
        name='20 MA', 
        line=dict(color='orange')
    ))
    fig.add_trace(go.Scatter(
        x=df['date'], 
        y=ma50, 
        name='50 MA', 
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis=dict(
            title="Date",
            type='date'
        ),
        yaxis=dict(
            title="Price (USD)",
            tickformat='$,.2f'
        )
    )
    
    try:
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.error(f"Error serializing candlestick chart: {str(e)}")
        return None

def create_volume_chart(df):
    if df.empty:
        return None

    try:
        fig = go.Figure(data=[
            go.Bar(
                x=df['date'],
                y=df['volume'],
                name='Volume'
            )
        ])
        
        fig.update_layout(
            template='plotly_dark',
            height=300,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(
                title="Date",
                type='date'
            ),
            yaxis=dict(
                title="Volume"
            )
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except Exception as e:
        logger.error(f"Error creating volume chart: {str(e)}")
        return None

@app.route('/')
def index():
    # Get available tickers for initial load
    stocks = get_available_tickers('stock')
    etfs = get_available_tickers('etf')
    cryptos = get_available_tickers('crypto')
    
    # Set default dates
    default_end = datetime.now()
    default_start = default_end - timedelta(days=30)  # Last 30 days by default
    
    return render_template('index.html', 
                         default_start=default_start.strftime('%Y-%m-%d'),
                         default_end=default_end.strftime('%Y-%m-%d'),
                         stocks=stocks,
                         etfs=etfs,
                         cryptos=cryptos)

@app.route('/get_tickers/<asset_type>')
def get_tickers(asset_type):
    tickers = get_available_tickers(asset_type)
    return jsonify(tickers)

@app.route('/get_data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        ticker = data.get('ticker', 'AAPL').upper()
        asset_type = data.get('asset_type', 'stock')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        logger.info(f"Received request with data: {data}")

        # Validate dates
        try:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            min_date = datetime(2020, 1, 1)
            max_date = datetime(2025, 8, 31)  # Set max date to August 2025

            if start_date_obj < min_date:
                return jsonify({
                    'error': f'Start date cannot be before 2020-01-01'
                }), 400
            if end_date_obj > max_date:
                return jsonify({
                    'error': f'End date cannot be after 2025-08-31'
                }), 400
            if start_date_obj > end_date_obj:
                return jsonify({
                    'error': 'Start date cannot be after end date'
                }), 400
        except ValueError as e:
            return jsonify({
                'error': f'Invalid date format: {str(e)}'
            }), 400

        logger.info(f"Fetching data for {ticker} ({asset_type}) from {start_date} to {end_date}")

        # Load data
        df = load_data_from_db(asset_type, ticker, start_date, end_date)
        
        if df.empty:
            return jsonify({
                'error': f'No data found for {ticker} between {start_date} and {end_date}'
            }), 404

        # Create charts
        candlestick_chart = create_candlestick_chart(df)
        volume_chart = create_volume_chart(df)

        if not candlestick_chart or not volume_chart:
            return jsonify({
                'error': 'Error creating charts'
            }), 500

        metrics = calculate_metrics(df)
        stats = df.describe().round(2).to_dict()

        return jsonify({
            'metrics': metrics,
            'candlestick_chart': candlestick_chart,
            'volume_chart': volume_chart,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

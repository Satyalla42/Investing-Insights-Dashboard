import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd

conn = psycopg2.connect(
    host="investing-insights-db1.cpmkiuwmc3bi.eu-north-1.rds.amazonaws.com",
    port=5432,
    database="investing_insights",
    user="postgres",
    password="zuhvij-1kasGe-dixgycT"
)

conn.autocommit = True  # Für vereinfachtes Commit-Verhalten

def insert_data(df, table_name):
    # Daten in DB einfügen (Annahme: df-Spalten passen genau zu DB-Spalten)
    cols = ",".join(df.columns)
    # Platzhalter für insert
    vals_template = "(" + ",".join(["%s"] * len(df.columns)) + ")"
    vals = [tuple(x) for x in df.to_numpy()]
    
    with conn.cursor() as cur:
        query = f"INSERT INTO {table_name} ({cols}) VALUES %s ON CONFLICT DO NOTHING;"
        execute_values(cur, query, vals)
    print(f"✅ {len(vals)} rows inserted into {table_name}")

def fetch_and_save_stock(ticker, start="2020-01-01", end="2025-05-28"):
    stock = yf.Ticker(ticker)
    df = stock.history(start=start, end=end).reset_index()
    # Spalten passend für DB umbenennen/filtern
    df = df.rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close",
        "Volume": "volume", "Dividends": "dividends", "Stock Splits": "stock_splits"
    })[["date","open","high","low","close","volume","dividends","stock_splits"]]
    insert_data(df, "stock_data")

def fetch_and_save_etf(ticker, start="2020-01-01", end="2025-05-28"):
    etf = yf.Ticker(ticker)
    df = etf.history(start=start, end=end).reset_index()
    df = df.rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close",
        "Volume": "volume", "Dividends": "dividends", "Stock Splits": "stock_splits"
    })
    # ETF hat noch Capital Gains? yfinance liefert das nicht direkt, ggf. Spalte manuell hinzufügen (hier als 0)
    df["capital_gains"] = 0  
    df = df[["date","open","high","low","close","volume","dividends","stock_splits","capital_gains"]]
    insert_data(df, "etf_data")

def fetch_and_save_crypto(ticker="BTC-USD", start="2020-01-01", end="2025-05-28"):
    crypto = yf.Ticker(ticker)
    df = crypto.history(start=start, end=end).reset_index()
    df = df.rename(columns={
        "Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close",
        "Volume": "volume", "Dividends": "dividends", "Stock Splits": "stock_splits"
    })[["date","open","high","low","close","volume","dividends","stock_splits"]]
    insert_data(df, "crypto_data")

# Beispielaufruf
fetch_and_save_stock("AAPL")
fetch_and_save_etf("SPY")
fetch_and_save_crypto("BTC-USD")

conn.close()


# --- Load tickers from CSV ---

tickers_df = pd.read_csv("european_tickers_approx_2000.csv", header=None)  # no header assumed
tickers = tickers_df[0].tolist()

# Loop over tickers and fetch+save data (all as stocks here)
for ticker in tickers:
    try:
        fetch_and_save_stock(ticker)
        print(f"✅ Successfully processed {ticker}")
    except Exception as e:
        print(f"❌ Error processing {ticker}: {e}")

conn.close()
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
from datetime import datetime
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_fetcher.log'),
        logging.StreamHandler()
    ]
)

# Database configuration - hardcoded for testing
DB_CONFIG = {
    "host": "investing-insights-db1.cpmkiuwmc3bi.eu-north-1.rds.amazonaws.com",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": ,
    "sslmode": "require"
}

class DatabaseConnection:
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.conn = None

    def connect(self) -> None:
        try:
            self.conn = psycopg2.connect(**self.config)
            self.conn.autocommit = True
            logging.info("Database connection established successfully")
        except Exception as e:
            logging.error(f"Database connection failed: {str(e)}")
            raise

    def close(self) -> None:
        if self.conn:
            self.conn.close()
            logging.info("Database connection closed")

    def __enter__(self):
        self.connect()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class DataFetcher:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.column_mapping = {
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume",
            "Dividends": "dividends",
            "Stock Splits": "stock_splits"
        }

    def _insert_data(self, df: pd.DataFrame, table_name: str, ticker: str) -> None:
        if df.empty:
            logging.warning(f"No data to insert for {ticker}")
            return

        if 'ticker' not in df.columns:
            df['ticker'] = ticker

        cols = ",".join(df.columns)
        vals = [tuple(x) for x in df.to_numpy()]

        with DatabaseConnection(self.db_config) as conn:
            with conn.cursor() as cur:
                try:
                    query = f"INSERT INTO {table_name} ({cols}) VALUES %s ON CONFLICT DO NOTHING;"
                    execute_values(cur, query, vals)
                    logging.info(f"✅ {len(vals)} rows inserted into {table_name} for {ticker}")
                except Exception as e:
                    logging.error(f"Error inserting data for {ticker}: {str(e)}")
                    raise

    def _fetch_data(self, ticker: str, start: str, end: str) -> Optional[pd.DataFrame]:
        try:
            asset = yf.Ticker(ticker)
            df = asset.history(start=start, end=end)

            if df.empty:
                logging.warning(f"No data retrieved for {ticker}")
                return None

            df = df.reset_index()
            df = df.rename(columns=self.column_mapping)
            return df
        except Exception as e:
            logging.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def fetch_and_save_stock(self, ticker: str, start: str, end: str) -> None:
        df = self._fetch_data(ticker, start, end)
        if df is not None:
            df = df[["date", "open", "high", "low", "close", "volume", "dividends", "stock_splits"]]
            self._insert_data(df, "stock_data", ticker)

    def fetch_and_save_etf(self, ticker: str, start: str, end: str) -> None:
        df = self._fetch_data(ticker, start, end)
        if df is not None:
            df["capital_gains"] = 0
            df = df[["date", "open", "high", "low", "close", "volume", "dividends", "stock_splits", "capital_gains"]]
            self._insert_data(df, "etf_data", ticker)

    def fetch_and_save_crypto(self, ticker: str, start: str, end: str) -> None:
        df = self._fetch_data(ticker, start, end)
        if df is not None:
            df = df[["date", "open", "high", "low", "close", "volume", "dividends", "stock_splits"]]
            self._insert_data(df, "crypto_data", ticker)

def process_ticker(fetcher: DataFetcher, ticker: str, asset_type: str = "stock") -> None:
    start = "2020-01-01"
    end = datetime.now().strftime("%Y-%m-%d")

    try:
        if asset_type == "stock":
            fetcher.fetch_and_save_stock(ticker, start, end)
        elif asset_type == "etf":
            fetcher.fetch_and_save_etf(ticker, start, end)
        elif asset_type == "crypto":
            fetcher.fetch_and_save_crypto(ticker, start, end)
        else:
            logging.warning(f"Unknown asset_type '{asset_type}' for ticker {ticker}")
            return
        logging.info(f"✅ Successfully processed {ticker} as {asset_type}")
    except Exception as e:
        logging.error(f"❌ Error processing {ticker}: {str(e)}")

def main():
    fetcher = DataFetcher(DB_CONFIG)

    # Optional: Einzelne Test-Ticker
    process_ticker(fetcher, "AAPL", "stock")
    process_ticker(fetcher, "SPY", "etf")
    process_ticker(fetcher, "BTC-USD", "crypto")

    # Bulk-Verarbeitung aus CSV
    try:
        tickers_df = pd.read_csv("cleaned_tickers.csv")

        # Normalize column names to lowercase
        tickers_df.columns = tickers_df.columns.str.lower()

        if "ticker" not in tickers_df.columns or "type" not in tickers_df.columns:
            logging.error("CSV file must contain 'ticker' and 'type' columns (lowercase)")
            return

        with ThreadPoolExecutor(max_workers=5) as executor:
            for _, row in tickers_df.iterrows():
                ticker = row["ticker"]
                asset_type = str(row["type"]).strip().lower()
                if asset_type not in {"stock", "etf", "crypto"}:
                    logging.warning(f"Skipping ticker {ticker} with unknown type '{asset_type}'")
                    continue
                executor.submit(process_ticker, fetcher, ticker, asset_type)
                time.sleep(0.5)  # Rate limiting

    except FileNotFoundError:
        logging.error("Tickers CSV file 'cleaned_tickers.csv' not found")
    except Exception as e:
        logging.error(f"Error processing bulk tickers: {str(e)}")

    logging.info("✅ Datenimport abgeschlossen")

if __name__ == "__main__":
    main()

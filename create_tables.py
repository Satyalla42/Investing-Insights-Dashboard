import psycopg2

# Database configuration - hardcoded for testing
DB_CONFIG = {
    "host": "investing-insights-db1.cpmkiuwmc3bi.eu-north-1.rds.amazonaws.com",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password":,
    "sslmode": "require"
}

# Table creation SQL statements
create_stock_table = """
CREATE TABLE IF NOT EXISTS stock_data (
    ticker VARCHAR(10),
    date DATE,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    dividends NUMERIC,
    stock_splits NUMERIC
);
"""

create_etf_table = """
CREATE TABLE IF NOT EXISTS etf_data (
    ticker VARCHAR(10),
    date DATE,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    dividends NUMERIC,
    stock_splits NUMERIC,
    capital_gains NUMERIC
);
"""

create_crypto_table = """
CREATE TABLE IF NOT EXISTS crypto_data (
    ticker VARCHAR(10),
    date DATE,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT,
    dividends NUMERIC,
    stock_splits NUMERIC
);
"""

# Connect and execute
try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute(create_stock_table)
    cursor.execute(create_etf_table)
    cursor.execute(create_crypto_table)

    print("✅ Tables created or already exist.")

except Exception as e:
    print("❌ Error:", e)

finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

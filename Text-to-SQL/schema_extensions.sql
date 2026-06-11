-- Optional extension tables (Notes: Ethereum + third-party pricing data)

CREATE TABLE IF NOT EXISTS ethereum_blocks (
    number          INTEGER PRIMARY KEY,
    hash            TEXT NOT NULL UNIQUE,
    parent_hash     TEXT,
    timestamp       INTEGER NOT NULL,
    gas_used        INTEGER,
    gas_limit       INTEGER,
    miner           TEXT,
    transaction_count INTEGER
);

CREATE TABLE IF NOT EXISTS btc_daily_prices (
    date            TEXT PRIMARY KEY,
    price_usd       REAL NOT NULL,
    source          TEXT NOT NULL
);

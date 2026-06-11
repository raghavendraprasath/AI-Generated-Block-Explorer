PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS blocks (
    height              INTEGER PRIMARY KEY,
    hash                TEXT NOT NULL UNIQUE,
    confirmations       INTEGER,
    version             INTEGER,
    version_hex         TEXT,
    merkleroot          TEXT,
    time                INTEGER NOT NULL,
    mediantime          INTEGER,
    nonce               INTEGER,
    bits                TEXT,
    target              TEXT,
    difficulty          REAL,
    chainwork           TEXT,
    ntx                 INTEGER,
    previousblockhash   TEXT,
    nextblockhash       TEXT,
    strippedsize        INTEGER,
    size                INTEGER,
    weight              INTEGER
);

CREATE TABLE IF NOT EXISTS coinbase_tx (
    block_height    INTEGER PRIMARY KEY,
    version         INTEGER,
    locktime        INTEGER,
    sequence        INTEGER,
    coinbase        TEXT,
    FOREIGN KEY (block_height) REFERENCES blocks(height)
);

CREATE TABLE IF NOT EXISTS transactions (
    txid            TEXT PRIMARY KEY,
    block_height    INTEGER NOT NULL,
    hash            TEXT,
    version         INTEGER,
    size            INTEGER,
    vsize           INTEGER,
    weight          INTEGER,
    locktime        INTEGER,
    fee             REAL,
    hex             TEXT,
    FOREIGN KEY (block_height) REFERENCES blocks(height)
);

CREATE TABLE IF NOT EXISTS transaction_inputs (
    txid                TEXT NOT NULL,
    vin_index           INTEGER NOT NULL,
    is_coinbase         INTEGER NOT NULL DEFAULT 0,
    spent_txid          TEXT,
    spent_vout          INTEGER,
    coinbase            TEXT,
    scriptsig_asm       TEXT,
    scriptsig_hex       TEXT,
    sequence            INTEGER,
    txinwitness         TEXT,
    PRIMARY KEY (txid, vin_index),
    FOREIGN KEY (txid) REFERENCES transactions(txid)
);

CREATE TABLE IF NOT EXISTS transaction_outputs (
    txid                 TEXT NOT NULL,
    vout_index           INTEGER NOT NULL,
    value                REAL NOT NULL,
    scriptpubkey_asm     TEXT,
    scriptpubkey_desc    TEXT,
    scriptpubkey_hex     TEXT,
    scriptpubkey_address TEXT,
    scriptpubkey_type    TEXT,
    PRIMARY KEY (txid, vout_index),
    FOREIGN KEY (txid) REFERENCES transactions(txid)
);

CREATE TABLE IF NOT EXISTS sync_state (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);
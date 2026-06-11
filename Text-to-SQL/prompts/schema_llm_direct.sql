CREATE TABLE bitcoin_tx (
  txid TEXT PRIMARY KEY,
  hash TEXT,
  version INTEGER,
  size INTEGER,
  vsize INTEGER,
  weight INTEGER,
  locktime INTEGER,
  vin TEXT[],
  vout TEXT[],
  fee REAL,
  hex TEXT,
  scriptPubKey TEXT,
  address TEXT,
  scriptSig TEXT,
  description TEXT,
  timestamp INTEGER
);

CREATE TABLE bitcoin_vin (
  vin TEXT PRIMARY KEY,
  txid TEXT,
  vout TEXT[],
  scriptSig TEXT,
  address TEXT,
  description TEXT,
  timestamp INTEGER
);

CREATE TABLE bitcoin_vout (
  vout TEXT PRIMARY KEY,
  value REAL,
  n INTEGER,
  scriptPubKey TEXT,
  address TEXT,
  description TEXT,
  timestamp INTEGER
);

CREATE INDEX idx_tx_hash ON bitcoin_tx (hash);
CREATE INDEX idx_vin_hash ON bitcoin_vin (hash);
CREATE INDEX idx_vout_hash ON bitcoin_vout (value);

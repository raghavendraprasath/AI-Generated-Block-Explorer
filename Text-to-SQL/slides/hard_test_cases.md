# Text-to-SQL Hard Failure Cases — Class Slide

**INFO7500 Homework 3** | SpiderV2: https://spider2-sql.github.io/

All three cases below were verified with **`run_tests.py --live`** and/or executing the incorrect SQL on `blockchain.db`.

---

## Case 1 — Returns height instead of hash

**Question:** What is the hash of the block at the maximum height?

| | |
|---|---|
| **Correct SQL** | `SELECT hash FROM blocks ORDER BY height DESC LIMIT 1` |
| **Correct answer** | `000000000003ba27aa200b1cecaad478d2b00432346c3f1f3986da1afd33e506` |
| **Our system generated** | `SELECT blocks.height FROM blocks WHERE height = (SELECT MAX(height) FROM blocks)` |
| **Wrong answer** | **100000** |

**Why it fails:** The model answered with **height** when the question asked for **hash**.

---

## Case 2 — Wrong aggregation for “most transactions”

**Question:** Which block height has the most transactions?

| | |
|---|---|
| **Correct SQL** | `SELECT block_height FROM transactions GROUP BY block_height ORDER BY COUNT(*) DESC LIMIT 1` |
| **Correct answer** | **93107** |
| **Our system generated** | `SELECT MAX(block_height) FROM transactions` |
| **Wrong answer** | **100000** |

**Why it fails:** Highest block with *any* transaction ≠ block with the *most* transactions.

---

## Case 3 — P2PK vs P2PKH script types

**Question:** What is the total BTC value of all pubkeyhash (P2PKH) outputs?

| | |
|---|---|
| **Correct SQL** | `SELECT ROUND(SUM(value), 4) FROM transaction_outputs WHERE scriptpubkey_type = 'pubkeyhash'` |
| **Correct answer** | **18,963,002.1219 BTC** |
| **Our system generated** | `SELECT ROUND(SUM(value), 4) FROM transaction_outputs WHERE scriptpubkey_type = 'pubkey'` |
| **Wrong answer** | **5,486,359.0599 BTC** |

**Why it fails:** Bitcoin Core uses distinct `scriptpubkey_type` strings; confusing P2PK and P2PKH changes the total by millions of BTC.

---

## Takeaway

Even with schema in context, free-model text-to-SQL fails on column selection, aggregation logic, and domain-specific enums — similar to limits shown on the [Spider 2.0 leaderboard](https://spider2-sql.github.io/).

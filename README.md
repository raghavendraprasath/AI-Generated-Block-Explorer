# AI-Generated Block Explorer

An AI-powered Bitcoin Block Explorer developed as part of **INFO7500: Cryptocurrency and Smart Contracts** at Northeastern University.

<p align="center">
  <strong>Block Explorer AI</strong> — natural language · SQL · on-chain answers
</p>

<p align="center">
  <a href="Text-to-SQL/screenshots/ui_demo_home.png">
    <img src="Text-to-SQL/screenshots/ui_demo_home.png" alt="Home — chat" width="30%" />
  </a>
  <a href="Text-to-SQL/screenshots/ui_demo_charts.png">
    <img src="Text-to-SQL/screenshots/ui_demo_charts.png" alt="Insights — charts" width="30%" />
  </a>
  <a href="Text-to-SQL/screenshots/ui_demo_examples.png">
    <img src="Text-to-SQL/screenshots/ui_demo_examples.png" alt="Samples — starter questions" width="30%" />
  </a>
</p>

<p align="center">
  <em>Home</em> &nbsp;·&nbsp; <em>Insights</em> &nbsp;·&nbsp; <em>Samples</em>
</p>

```bash
cd Text-to-SQL && ./scripts/run_web_ui.sh ~/hw3-data/blockchain.db
# → http://localhost:8501
```

---

## Project Goal

The objective of this project is to build a blockchain explorer that combines Bitcoin blockchain data with Large Language Models (LLMs) to enable natural language interaction with blockchain information.

Users will be able to ask questions such as:

> How many blocks were mined today?

> What is the latest block height?

> Which block contains the most transactions?

The system will translate natural language questions into SQL queries and retrieve blockchain data automatically.

---

## Technology Stack

- Bitcoin Core
- Bitcoin RPC
- Docker
- Python
- SQLite
- OpenRouter
- Large Language Models (LLMs)
- Streamlit (Block Explorer AI web UI)

---

## Project Roadmap

### Week 2
Tooling for AI-Generated Block Explorer (`Tooling-for-AI-Generated-Block-Explorer/`)

- Docker setup
- Bitcoin Core build from source
- Bitcoin RPC validation
- LLM Text-to-SQL prototype

### Week 3
Text-to-SQL (`Text-to-SQL/`)

- SQLite schema from `getblock(hash, 2)` JSON
- Deterministic ingestion + scheduled updater
- Natural language → SQL → answers (OpenRouter)
- Test suite (12 golden cases), hard-failure analysis, **Block Explorer AI** UI, charts
- Class slides: `Text-to-SQL/slides/hard_failures.pptx`

See [`Text-to-SQL/README.md`](Text-to-SQL/README.md) for full documentation, architecture, and screenshots.

---

## Course

INFO7500 – Cryptocurrency and Smart Contracts

Northeastern University

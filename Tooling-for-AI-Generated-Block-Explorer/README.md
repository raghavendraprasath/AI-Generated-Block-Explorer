# Tooling for AI-Generated Block Explorer

## INFO7500 – Cryptocurrency and Smart Contracts

**Student:** Raghavendra Prasath Sridhar

---

# Assignment Overview

This assignment focused on setting up and validating the core technologies required for building an AI-Generated Bitcoin Block Explorer.

The objective was not to build the final application, but to establish the foundational tooling that will support future development throughout the semester.

Three major technologies were explored:

1. Docker
2. Bitcoin Core (bitcoind)
3. LLM-Based Text-to-SQL Generation

---

# Environment

| Component             | Details           |
| --------------------- | ----------------- |
| Host Operating System | Windows 11        |
| Linux Environment     | Ubuntu WSL2       |
| Container Platform    | Docker Desktop    |
| Programming Language  | Python 3          |
| Blockchain Software   | Bitcoin Core      |
| AI Platform           | OpenRouter        |
| SDK                   | OpenAI Python SDK |

---

# Part 1 – Docker Setup

## Objective

Verify that Docker is correctly installed and capable of running Python applications inside containers.

## Files

```text
Dockerfile
hello_docker.py
```

## Dockerfile

The Dockerfile creates a lightweight Python environment and executes a simple Python script.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY hello_docker.py .

CMD ["python", "hello_docker.py"]
```

## Build Command

```bash
docker build -t hello-docker .
```

## Run Command

```bash
docker run hello-docker
```

## Validation

The Docker image was successfully built and executed.

### Docker Build

![Docker Build](screenshots/docker_build.png)

### Docker Run

![Docker Run](screenshots/docker_run.png)

---

# Part 2 – Bitcoin Core Build from Source

## Objective

Clone, compile, test, configure, and run Bitcoin Core from source code.

Building from source provides hands-on experience with the Bitcoin software stack and demonstrates understanding of blockchain node infrastructure.

---

## Clone Bitcoin Core Repository

```bash
git clone https://github.com/bitcoin/bitcoin.git
cd bitcoin
```

---

## Configure Bitcoin Core

Bitcoin Core was configured with GUI and wallet support enabled.

```bash
cmake -B build-gui \
  -DBUILD_GUI=ON \
  -DWITH_ZMQ=OFF \
  -DENABLE_IPC=OFF
```

---

## Build Bitcoin Core

```bash
cmake --build build-gui -j2
```

---

## Generated Binaries

The build process successfully produced:

```text
bitcoin
bitcoin-cli
bitcoin-qt
bitcoin-wallet
bitcoin-tx
bitcoin-util
bitcoind
```

### Screenshot – Successful Build

![Bitcoin Build](screenshots/bitcoin_build.png)

---

# Version Verification

Verified the generated binaries.

## Commands

```bash
./build-gui/bin/bitcoin-qt --version

./build-gui/bin/bitcoind --version

./build-gui/bin/bitcoin-cli --version
```

### Screenshot – Version Verification

![Bitcoin Version](screenshots/bitcoin_version.png)

---

# Bitcoin Core Testing

Executed the Bitcoin Core test suite to verify the integrity of the build.

## Command

```bash
ctest --test-dir build-gui
```

## Result

```text
100% tests passed
348 tests passed
0 tests failed
```

### Screenshot – Test Results

![Bitcoin Tests](screenshots/bitcoin_tests.png)

---

# Bitcoin Configuration

Created the Bitcoin Core configuration file.

## File Location

```text
~/.bitcoin/bitcoin.conf
```

## Configuration

```text
server=1
rpcuser=test
rpcpassword=test
```

### Screenshot – bitcoin.conf

![Bitcoin Configuration](screenshots/bitcoin_conf.png)

---

# Running Bitcoin Core

Started Bitcoin Core in daemon mode.

## Command

```bash
./build-gui/bin/bitcoind -daemon
```

The node started successfully and began network synchronization.

---

# RPC Verification

Verified Bitcoin Core Remote Procedure Call (RPC) functionality.

## Commands

```bash
./build-gui/bin/bitcoin-cli getblockcount

./build-gui/bin/bitcoin-cli getblockchaininfo
```

The commands successfully returned blockchain information and confirmed communication between bitcoin-cli and bitcoind.

### Screenshot – RPC Verification

![RPC Commands](screenshots/rpc_commands.png)

---

# Debug Log Verification

Bitcoin Core generated runtime logs successfully.

## Log Location

```text
~/.bitcoin/debug.log
```

The log captures:

* Node startup
* Peer connections
* Synchronization progress
* RPC activity
* Shutdown operations

### Screenshot – Debug Log

![Debug Log](screenshots/debug_log.png)

---

# Part 3 – LLM-Based Text-to-SQL Generation

## Objective

Create a Python application that converts natural language questions into SQL queries using a Large Language Model.

## File

```text
text_to_sql.py
```

## AI Platform

The implementation uses:

* OpenRouter API
* OpenAI-compatible SDK
* Python

---

## Database Schema

A simplified Bitcoin-inspired schema was provided to the model.

### Tables

```sql
CREATE TABLE blocks (
    height INTEGER PRIMARY KEY,
    hash TEXT NOT NULL,
    time INTEGER NOT NULL,
    tx_count INTEGER NOT NULL
);

CREATE TABLE transactions (
    txid TEXT PRIMARY KEY,
    block_height INTEGER NOT NULL,
    value REAL,
    fee REAL
);
```

---

## Example Queries

### Question

```text
How many blocks are stored in the blocks table?
```

### Generated SQL

```sql
SELECT COUNT(*) FROM blocks;
```

---

### Question

```text
What is the highest block height?
```

### Generated SQL

```sql
SELECT MAX(height) FROM blocks;
```

---

### Question

```text
Show the hash and timestamp of the latest block.
```

### Generated SQL

```sql
SELECT hash, time
FROM blocks
ORDER BY height DESC
LIMIT 1;
```

---

## Screenshot – Text-to-SQL Output

![Text to SQL](screenshots/text_to_sql.png)

---

# Screenshots Gallery

Below are thumbnails of all screenshots in `Tooling-for-AI-Generated-Block-Explorer/Screenshots/`, with a short description for each.

> Note: This README also references a separate `screenshots/` folder (lowercase) for inline evidence images used throughout the write-up. The gallery below is specifically for the `Screenshots/` (capital S) folder.

| Thumbnail | Description |
|---|---|
| [![Bitcoin Core Built](Screenshots/Bitcoin%20Core%20Built.png)](Screenshots/Bitcoin%20Core%20Built.png) | Bitcoin Core successfully built/compiled from source (build completion output). |
| [![Bitcoin Core Tests](Screenshots/Bitcoin%20Core%20Tests.png)](Screenshots/Bitcoin%20Core%20Tests.png) | Bitcoin Core test suite execution results showing tests passed. |
| [![Bitcoin Core Version](Screenshots/Bitcoin%20Core%20Version.png)](Screenshots/Bitcoin%20Core%20Version.png) | Version verification of built Bitcoin Core binaries (e.g., `bitcoind`, `bitcoin-cli`, `bitcoin-qt`). |
| [![Bitcoin Process Stopped](Screenshots/Bitcoin%20Process%20Stopped.png)](Screenshots/Bitcoin%20Process%20Stopped.png) | Example of stopping the Bitcoin process / daemon shutdown output. |
| [![Dockerfile Screenshot](Screenshots/Dockerfile%20Screenshot.png)](Screenshots/Dockerfile%20Screenshot.png) | Dockerfile contents used to build the Python container image. |
| [![Text-To-SQL Prompt](Screenshots/Text-To-SQL%20Prompt.png)](Screenshots/Text-To-SQL%20Prompt.png) | Text-to-SQL prompt/example interaction used for generating SQL from natural language. |
| [![bitcoin conf created](Screenshots/bitcoin%20conf%20created.png)](Screenshots/bitcoin%20conf%20created.png) | Creation of `bitcoin.conf` configuration file (RPC/server settings). |
| [![bitcoin-cli RPC working](Screenshots/bitcoin-cli%20RPC%20working.png)](Screenshots/bitcoin-cli%20RPC%20working.png) | Successful RPC call via `bitcoin-cli`, confirming node connectivity and RPC credentials. |
| [![bitcoind running](Screenshots/bitcoind%20running.png)](Screenshots/bitcoind%20running.png) | `bitcoind` running (daemon started) and initial runtime output. |
| [![curl RPC command](Screenshots/curl%20RPC%20command.png)](Screenshots/curl%20RPC%20command.png) | RPC verification using a raw `curl` JSON-RPC command. |
| [![debug log proof](Screenshots/debug%20log%20proof.png)](Screenshots/debug%20log%20proof.png) | Proof/debug output showing `~/.bitcoin/debug.log` activity (node + RPC events). |

---

# Deliverables

This folder contains:

```text
Tooling-for-AI-Generated-Block-Explorer/
│
├── README.md
├── Dockerfile
├── hello_docker.py
├── text_to_sql.py
├── debug.log
│
└── screenshots/
```

---

# Learning Outcomes

This assignment provided practical experience with:

* Docker containerization
* Building Bitcoin Core from source
* Bitcoin node configuration
* Bitcoin RPC communication
* Blockchain infrastructure tooling
* Python development
* LLM API integration
* Natural Language to SQL generation

---

# Conclusion

The required tooling for the AI-Generated Block Explorer project was successfully installed, configured, tested, and documented.

The environment is now prepared for future milestones involving blockchain data extraction, database integration, AI-assisted querying, and development of a complete Bitcoin Block Explorer applic[...]

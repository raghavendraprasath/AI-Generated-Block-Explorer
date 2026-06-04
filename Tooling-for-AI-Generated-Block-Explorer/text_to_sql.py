import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

schema = """
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
    fee REAL,
    FOREIGN KEY (block_height) REFERENCES blocks(height)
);
"""

questions = [
    "How many blocks are stored in the blocks table?",
    "What is the highest block height?",
    "Show the hash and time of the latest block.",
    "How many transactions are stored for each block?",
    "Which block has the most transactions?"
]

for question in questions:
    prompt = f"""
You are given this SQLite schema:

{schema}

Convert the following natural language question into a SQL query:

Question: {question}

Only return the SQL query. Do not explain.
"""

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": "You are a SQL developer. You only return valid SQLite SQL."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    print("Question:")
    print(question)
    print("\nGenerated SQL:")
    print(response.choices[0].message.content)
    print("-" * 60)
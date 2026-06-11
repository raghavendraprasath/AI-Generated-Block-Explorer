#!/usr/bin/env python3
"""Streamlit web chat UI for Bitcoin Text-to-SQL (Notes: Chat UI)."""

import os
from pathlib import Path

import streamlit as st

from project_env import get_openrouter_api_key, load_project_env
from text_to_sql import CANNOT_ANSWER, DEFAULT_MODEL, answer_question

load_project_env()

DEFAULT_DB = os.environ.get(
    "HW3_DB_PATH",
    "/home/adity/hw3-data/blockchain.db",
)


def main() -> None:
    st.set_page_config(
        page_title="Bitcoin Text-to-SQL",
        page_icon="₿",
        layout="centered",
    )
    st.title("Bitcoin Block Explorer")
    st.caption("Natural language questions → SQL → answers from your SQLite database")

    with st.sidebar:
        st.header("Settings")
        db_input = st.text_input("Database path (absolute)", value=DEFAULT_DB)
        model = st.text_input(
            "OpenRouter model",
            value=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
            help="openrouter/free is slow (30–90s). Try google/gemma-2-9b-it:free or a paid model.",
        )
        api_key = get_openrouter_api_key()
        if not api_key:
            st.error("Set OPENROUTER_API_KEY in Text-to-SQL/.env")
        else:
            st.success(f"API key loaded ({api_key[:12]}…)")
        st.markdown("---")
        st.markdown("**CLI alternative:** `python3 chat.py --db <path>`")
        if st.button("Clear chat"):
            st.session_state.messages = []
            st.rerun()

    db_path = Path(db_input).expanduser()
    if not db_path.is_absolute():
        st.warning("Database path must be absolute.")
        return
    if not db_path.exists():
        st.warning(f"Database not found: `{db_path}`")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sql"):
                st.code(message["sql"], language="sql")

    prompt = st.chat_input("Ask about blocks, transactions, fees, prices…")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_key = get_openrouter_api_key()
        if not api_key:
            st.error("OPENROUTER_API_KEY missing — check Text-to-SQL/.env")
            return
        try:
            with st.spinner("Calling OpenRouter LLM (free models can take 30–90 seconds)…"):
                result = answer_question(
                    prompt, db_path.resolve(), api_key=api_key, model=model
                )
        except Exception as exc:
            st.error(str(exc))
            return

        if result.get("cannot_answer"):
            st.warning(CANNOT_ANSWER)
            st.session_state.messages.append(
                {"role": "assistant", "content": CANNOT_ANSWER, "sql": None}
            )
            return

        sql = result["sql"]
        answer = result.get("answer", "")
        st.code(sql, language="sql")
        st.markdown(f"**Answer:** {answer}")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"**Answer:** {answer}", "sql": sql}
        )


if __name__ == "__main__":
    main()

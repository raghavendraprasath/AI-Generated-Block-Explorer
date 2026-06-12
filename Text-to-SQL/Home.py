#!/usr/bin/env python3
"""Block Explorer AI — Home (natural-language chat over SQLite)."""

import os
from pathlib import Path

import streamlit as st

from project_env import get_openrouter_api_key, load_project_env
from text_to_sql import CANNOT_ANSWER, DEFAULT_MODEL, answer_question
from ui_shared import inject_theme, render_page_header, render_settings_sidebar

load_project_env()

DEFAULT_DB = os.environ.get("HW3_DB_PATH", "/home/adity/hw3-data/blockchain.db")


def main() -> None:
    st.set_page_config(
        page_title="Home · Block Explorer AI",
        page_icon="₿",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    inject_theme()

    with st.sidebar:
        db_path = render_settings_sidebar(show_clear_chat=True)

    render_page_header(
        "Home",
        "Questions in plain English — answers from your synced Bitcoin database.",
        badge="Live chat",
    )

    if db_path is None:
        st.info("Set a valid database path in the sidebar to start.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sql"):
                st.code(message["sql"], language="sql")

    prompt = st.chat_input("Blocks, transactions, fees, prices…")
    if not prompt:
        return

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        api_key = get_openrouter_api_key()
        model = st.session_state.get(
            "sidebar_model", os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL)
        )
        if not api_key:
            st.error("OPENROUTER_API_KEY missing — check Text-to-SQL/.env")
            return
        try:
            with st.spinner("Thinking…"):
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
        st.markdown(f"**{answer}**")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"**{answer}**", "sql": sql}
        )


if __name__ == "__main__":
    main()

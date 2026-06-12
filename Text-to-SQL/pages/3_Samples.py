"""Block Explorer AI — Samples (curated starter queries)."""

import streamlit as st

from project_env import get_openrouter_api_key
from text_to_sql import CANNOT_ANSWER, answer_question
from ui_shared import (
    get_sidebar_model,
    inject_theme,
    load_example_groups,
    render_page_header,
    render_settings_sidebar,
)

st.set_page_config(
    page_title="Samples · Block Explorer AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

with st.sidebar:
    db_path = render_settings_sidebar()

if db_path is None:
    st.stop()

render_page_header(
    "Samples",
    "Curated questions to explore the database — run any with one click.",
    badge="Starters",
)

groups = load_example_groups()
category = st.selectbox("Topic", list(groups.keys()))
cases = groups[category]

st.caption(f"{len(cases)} sample questions")

for index, case in enumerate(cases, start=1):
    question = case["question"]
    st.markdown(f"**{index}. {question}**")
    if case.get("reason"):
        st.caption(case["reason"])

    if st.button("Run query", key=f"run_{category}_{index}", type="primary"):
        api_key = get_openrouter_api_key()
        if not api_key:
            st.error("OPENROUTER_API_KEY missing — check .env")
        else:
            try:
                with st.spinner("Running…"):
                    result = answer_question(
                        question,
                        db_path,
                        api_key=api_key,
                        model=get_sidebar_model(),
                    )
                if result.get("cannot_answer"):
                    st.success(CANNOT_ANSWER)
                else:
                    st.code(result["sql"], language="sql")
                    st.markdown(f"**{result.get('answer', '')}**")
            except Exception as exc:
                st.error(str(exc))

    st.divider()

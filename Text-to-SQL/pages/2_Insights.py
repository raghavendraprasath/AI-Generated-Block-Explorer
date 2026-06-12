"""Block Explorer AI — Insights (charts & visualizations)."""

import streamlit as st

from charts import CHART_PRESETS, build_figure, fetch_chart_data
from project_env import get_openrouter_api_key
from text_to_sql import CANNOT_ANSWER
from ui_shared import get_sidebar_model, inject_theme, render_page_header, render_settings_sidebar

st.set_page_config(
    page_title="Insights · Block Explorer AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_theme()

with st.sidebar:
    db_path = render_settings_sidebar()

if db_path is None:
    st.stop()

render_page_header(
    "Insights",
    "Turn queries into charts — block activity, fees, and market data at a glance.",
    badge="Visualize",
)

tab_quick, tab_custom = st.tabs(["Quick views", "Build your own"])

with tab_quick:
    st.caption("Ready-made views — instant, no LLM required.")
    preset_labels = [p["label"] for p in CHART_PRESETS]
    preset_idx = st.selectbox(
        "Select a view",
        range(len(preset_labels)),
        format_func=lambda i: preset_labels[i],
        label_visibility="collapsed",
    )
    if st.button("Render chart", type="primary", use_container_width=True):
        preset = CHART_PRESETS[preset_idx]
        try:
            sql, rows = fetch_chart_data(preset["question"], db_path, sql=preset["sql"])
            st.code(sql, language="sql")
            fig = build_figure(rows, preset["label"])
            st.pyplot(fig, clear_figure=True)
        except Exception as exc:
            st.error(str(exc))

with tab_custom:
    st.caption("Ask a question or paste SQL — results need **1 or 2 columns**.")
    custom_q = st.text_area(
        "Your question",
        placeholder="Heights and transaction counts for the first 20 blocks",
        height=72,
        label_visibility="collapsed",
    )
    use_llm = st.toggle("Generate SQL with AI", value=True)
    custom_sql = st.text_area(
        "SQL query",
        placeholder="SELECT height, ntx FROM blocks ORDER BY height ASC LIMIT 20",
        height=72,
        disabled=use_llm,
        label_visibility="collapsed",
    )

    if st.button("Render chart", key="custom_chart", use_container_width=True):
        if not custom_q.strip():
            st.warning("Enter a question for the chart title.")
        elif not get_openrouter_api_key() and use_llm:
            st.error("API key required for AI — toggle off or add OPENROUTER_API_KEY to .env")
        else:
            try:
                with st.spinner("Building chart…"):
                    sql, rows = fetch_chart_data(
                        custom_q.strip(),
                        db_path,
                        sql=None if use_llm else custom_sql.strip(),
                        api_key=get_openrouter_api_key(),
                        model=get_sidebar_model(),
                    )
                st.code(sql, language="sql")
                fig = build_figure(rows, custom_q.strip()[:80])
                st.pyplot(fig, clear_figure=True)
            except ValueError as exc:
                if str(exc) == CANNOT_ANSWER:
                    st.warning(CANNOT_ANSWER)
                else:
                    st.error(str(exc))
            except Exception as exc:
                st.error(str(exc))

"""Shared Streamlit branding, theme, and sidebar for Block Explorer AI."""

import json
import os
from pathlib import Path

import streamlit as st

from project_env import get_openrouter_api_key, load_project_env
from text_to_sql import DEFAULT_MODEL

load_project_env()

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = os.environ.get("HW3_DB_PATH", "/home/adity/hw3-data/blockchain.db")

PRODUCT_NAME = "Block Explorer AI"
PRODUCT_TAGLINE = "Natural language · SQL · On-chain answers"


def inject_theme() -> None:
    st.markdown(
        """
        <style>
          /* Page */
          .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 920px; }
          [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f1419 0%, #161b22 100%);
            border-right: 1px solid #30363d;
          }
          [data-testid="stSidebar"] .stMarkdown h1,
          [data-testid="stSidebar"] .stMarkdown h2,
          [data-testid="stSidebar"] .stMarkdown h3 { color: #e6edf3; }

          /* Product header */
          .bx-hero { margin-bottom: 1.75rem; }
          .bx-hero h1 {
            font-size: 2rem; font-weight: 700; letter-spacing: -0.03em;
            margin: 0 0 0.25rem 0; color: #e6edf3;
          }
          .bx-hero .bx-page {
            font-size: 1.1rem; font-weight: 600; color: #f7931a;
            margin: 0 0 0.5rem 0; letter-spacing: -0.01em;
          }
          .bx-hero p {
            margin: 0; color: #8b949e; font-size: 0.95rem;
          }
          .bx-pill {
            display: inline-block; margin-top: 0.65rem; padding: 0.2rem 0.65rem;
            border-radius: 999px; font-size: 0.72rem; font-weight: 600;
            letter-spacing: 0.04em; text-transform: uppercase;
            background: rgba(247, 147, 26, 0.15); color: #f7931a;
            border: 1px solid rgba(247, 147, 26, 0.35);
          }

          /* Sidebar brand */
          .bx-sidebar-brand { padding: 0.25rem 0 1rem 0; }
          .bx-sidebar-brand .name {
            font-size: 1.05rem; font-weight: 700; color: #e6edf3;
            letter-spacing: -0.02em;
          }
          .bx-sidebar-brand .tag { font-size: 0.75rem; color: #8b949e; margin-top: 0.15rem; }

          /* Section cards */
          .bx-section-label {
            font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em;
            text-transform: uppercase; color: #8b949e; margin-bottom: 0.5rem;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(page: str, subtitle: str, badge: str | None = None) -> None:
    """Main h1 is always PRODUCT_NAME; page is the section name (Home, Insights, …)."""
    badge_html = f'<span class="bx-pill">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="bx-hero">
          <h1>{PRODUCT_NAME}</h1>
          <p class="bx-page">{page}</p>
          <p>{subtitle}</p>
          {badge_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand() -> None:
    st.markdown(
        f"""
        <div class="bx-sidebar-brand">
          <div class="name">{PRODUCT_NAME}</div>
          <div class="tag">{PRODUCT_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_settings_sidebar(*, show_clear_chat: bool = False) -> Path | None:
    render_sidebar_brand()
    st.markdown('<p class="bx-section-label">Connection</p>', unsafe_allow_html=True)
    db_input = st.text_input("Database", value=DEFAULT_DB, help="Absolute path to blockchain.db")
    st.text_input(
        "Model",
        value=os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL),
        key="sidebar_model",
        help="OpenRouter model ID for LLM queries.",
    )
    api_key = get_openrouter_api_key()
    if not api_key:
        st.error("Add OPENROUTER_API_KEY to .env")
    else:
        st.success(f"Connected · {api_key[:10]}…")

    if show_clear_chat:
        st.markdown("---")
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")
    db_path = Path(db_input).expanduser()
    if not db_path.is_absolute():
        st.warning("Use an absolute database path.")
        return None
    if not db_path.exists():
        st.warning(f"Not found: `{db_path}`")
        return None
    return db_path.resolve()


def get_sidebar_model() -> str:
    return st.session_state.get("sidebar_model", DEFAULT_MODEL)


def load_example_groups() -> dict[str, list[dict]]:
    def load_json(name: str) -> list:
        return json.loads((ROOT / "tests" / name).read_text(encoding="utf-8"))

    return {
        "Bitcoin core": load_json("test_cases.json"),
        "Extensions": load_json("extension_cases.json"),
        "Out of scope": load_json("cannot_answer_cases.json"),
    }

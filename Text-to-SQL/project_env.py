"""Load secrets from .env in the project root (gitignored)."""

import os
from pathlib import Path


def load_project_env() -> None:
    """Load .env then .env.local. Called on every request (Streamlit-safe)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    root = Path(__file__).resolve().parent
    load_dotenv(root / ".env", override=True)
    load_dotenv(root / ".env.local", override=True)


def get_openrouter_api_key() -> str | None:
    """Return trimmed API key from environment / .env file."""
    load_project_env()
    key = (os.environ.get("OPENROUTER_API_KEY") or "").strip().strip('"').strip("'")
    return key or None

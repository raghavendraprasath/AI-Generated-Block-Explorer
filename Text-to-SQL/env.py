"""Backward-compatible shim — use project_env in new code."""

from project_env import get_openrouter_api_key, load_project_env

__all__ = ["get_openrouter_api_key", "load_project_env"]

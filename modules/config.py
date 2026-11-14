import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env", override=False)


def get_setting(name, default=None):
    """Read a setting from environment variables or Streamlit Cloud secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st
        value = st.secrets.get(name)
    except Exception:
        value = None

    return value if value not in (None, "") else default

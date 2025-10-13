"""Configuration pytest et fixtures globales."""

import sys
from unittest.mock import MagicMock

import pytest

# Mock Streamlit avant tous les imports
streamlit_mock = MagicMock()
sys.modules["streamlit"] = streamlit_mock


@pytest.fixture(autouse=True)
def reset_streamlit_mock():
    """Reset le mock Streamlit avant chaque test."""
    streamlit_mock.reset_mock()
    streamlit_mock.session_state = {}
    streamlit_mock.sidebar = MagicMock()
    streamlit_mock.container = MagicMock()
    streamlit_mock.columns = MagicMock()
    yield

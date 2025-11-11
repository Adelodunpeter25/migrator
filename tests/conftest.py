import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield Path(tmpdir)
        os.chdir(original_cwd)


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables"""

    def _set_env(key, value):
        monkeypatch.setenv(key, value)

    return _set_env

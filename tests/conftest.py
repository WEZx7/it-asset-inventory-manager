import importlib
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def app(tmp_path, monkeypatch):
    """Import main.py with its data file redirected to a temp directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(ROOT)
    sys.modules.pop("main", None)
    module = importlib.import_module("main")
    monkeypatch.setattr(module, "ASSETS_FILE", str(tmp_path / "assets.json"))
    module.assets = []
    yield module
    sys.modules.pop("main", None)

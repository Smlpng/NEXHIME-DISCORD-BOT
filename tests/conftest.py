import os
from pathlib import Path

import pytest


@pytest.fixture()
def players_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data_file = tmp_path / "players.json"
    monkeypatch.setenv("RPG50_DATA_FILE", str(data_file))
    return data_file
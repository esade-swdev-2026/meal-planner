from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point the app's working copy to a temporary file, so tests never touch data/."""
    data_file = tmp_path / "data" / "recipes.json"
    monkeypatch.setattr("meal_planner.cli.DATA_FILE", data_file)
    return data_file

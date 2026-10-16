import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.recipes import load_recipes

runner = CliRunner()


def test_invalid_filter_option_exits_with_error() -> None:
    result = runner.invoke(app, ["filter-meals"], input="7\n")

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "not a valid option" in result.output


def test_add_recipe_with_zero_cooking_time_exits_with_error() -> None:
    answers = "Test Toast\nbread\n1 slice\n\n0\n100\nToast it\n\n0\n"

    result = runner.invoke(app, ["add-recipe"], input=answers)

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "cooking time must be greater than zero" in result.output


def test_weekly_plan_with_too_low_calories_exits_with_error() -> None:
    result = runner.invoke(app, ["weekly-plan"], input="1\n")

    assert result.exit_code == 1
    assert isinstance(result.exception, SystemExit)
    assert "No recipes fit that calorie limit" in result.output


def test_load_recipes_rejects_broken_json(tmp_path: Path) -> None:
    path = tmp_path / "recipes.json"
    path.write_text("[{ this is not json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_recipes(path)


def test_load_recipes_rejects_recipe_with_missing_fields(tmp_path: Path) -> None:
    path = tmp_path / "recipes.json"
    path.write_text(json.dumps([{"name": "Toast"}]), encoding="utf-8")

    with pytest.raises(ValueError):
        load_recipes(path)


def test_load_recipes_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(OSError):
        load_recipes(tmp_path / "does_not_exist.json")

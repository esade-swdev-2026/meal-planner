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


def write_recipe(path: Path, **changes: object) -> None:
    recipe = {
        "name": "Toast",
        "ingredients": {"bread": "2 slices"},
        "cooking_time": 5,
        "calories": 200,
        "steps": ["Toast the bread"],
        "oven_temperature": None,
    }
    recipe.update(changes)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([recipe]), encoding="utf-8")


def test_load_recipes_accepts_a_valid_recipe(tmp_path: Path) -> None:
    path = tmp_path / "recipes.json"
    write_recipe(path)

    recipes = load_recipes(path)

    assert [recipe.name for recipe in recipes] == ["Toast"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "  ", "empty name"),
        ("ingredients", {}, "at least one ingredient"),
        ("ingredients", ["bread"], "ingredients"),
        ("ingredients", {"bread": 2}, "ingredients"),
        ("cooking_time", "fast", "cooking time"),
        ("cooking_time", 0, "cooking time"),
        ("cooking_time", True, "cooking time"),
        ("calories", -5, "calories"),
        ("calories", 2.5, "calories"),
        ("steps", [], "at least one step"),
        ("steps", "Toast the bread", "steps"),
        ("oven_temperature", "hot", "oven temperature"),
    ],
)
def test_load_recipes_rejects_fields_of_the_wrong_kind(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    path = tmp_path / "recipes.json"
    write_recipe(path, **{field: value})

    with pytest.raises(ValueError, match=message):
        load_recipes(path)


@pytest.mark.parametrize("content", ['{"name": "Toast"}', "null", "[1, 2]"])
def test_load_recipes_rejects_a_file_that_is_not_a_list_of_recipes(
    tmp_path: Path, content: str
) -> None:
    path = tmp_path / "recipes.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError):
        load_recipes(path)


@pytest.mark.parametrize("command", ["show", "fastest-meal", "count-recipes"])
def test_cli_reports_a_broken_recipes_file_without_a_traceback(
    isolated_data_file: Path, command: str
) -> None:
    write_recipe(isolated_data_file, cooking_time="fast")

    result = runner.invoke(app, [command])

    assert result.exit_code == 1
    assert "the recipes file is not valid" in result.output
    assert "cooking time" in result.output

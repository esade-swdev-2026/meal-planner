import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.logic import create_recipe
from meal_planner.recipes import SEED_FILE, Recipe, add_recipe, ensure_data_file, load_recipes


def test_create_recipe_builds_recipe() -> None:
    recipe = create_recipe(
        name="  Hummus ",
        ingredients={"chickpeas": "400 g"},
        cooking_time=10,
        calories=350,
        steps=["Blend everything"],
    )

    assert recipe.name == "Hummus"
    assert recipe.ingredients == {"chickpeas": "400 g"}
    assert recipe.oven_temperature is None


@pytest.mark.parametrize(
    ("name", "ingredients", "cooking_time", "calories", "steps", "oven"),
    [
        ("", {"bread": "1"}, 5, 100, ["Toast"], None),
        ("Toast", {}, 5, 100, ["Toast"], None),
        ("Toast", {"bread": "1"}, 5, 100, [], None),
        ("Toast", {"bread": "1"}, 0, 100, ["Toast"], None),
        ("Toast", {"bread": "1"}, 5, 0, ["Toast"], None),
        ("Toast", {"bread": "1"}, 5, 100, ["Toast"], -10),
    ],
)
def test_create_recipe_rejects_invalid_details(
    name: str,
    ingredients: dict[str, str],
    cooking_time: int,
    calories: int,
    steps: list[str],
    oven: int | None,
) -> None:
    with pytest.raises(ValueError):
        create_recipe(name, ingredients, cooking_time, calories, steps, oven)


@pytest.fixture
def recipes_file(tmp_path: Path) -> Path:
    path = tmp_path / "recipes.json"
    toast = {
        "name": "Toast",
        "ingredients": {"bread": "2 slices"},
        "cooking_time": 5,
        "calories": 200,
        "steps": ["Toast the bread"],
        "oven_temperature": None,
    }
    path.write_text(json.dumps([toast]), encoding="utf-8")
    return path


def test_add_recipe_saves_to_file(recipes_file: Path) -> None:
    soup = Recipe("Soup", {"tomatoes": "500 g"}, 30, 180, ["Simmer"])

    add_recipe(soup, recipes_file)

    names = [recipe.name for recipe in load_recipes(recipes_file)]
    assert names == ["Toast", "Soup"]


def test_add_recipe_rejects_duplicate_name(recipes_file: Path) -> None:
    duplicate = Recipe("toast", {"bread": "1 slice"}, 5, 100, ["Toast it"])

    with pytest.raises(ValueError):
        add_recipe(duplicate, recipes_file)

    assert len(load_recipes(recipes_file)) == 1


def test_ensure_data_file_copies_seed_when_missing(tmp_path: Path, recipes_file: Path) -> None:
    data_file = tmp_path / "data" / "recipes.json"

    result = ensure_data_file(data_file, seed_file=recipes_file)

    assert result == data_file
    assert data_file.read_text(encoding="utf-8") == recipes_file.read_text(encoding="utf-8")


def test_ensure_data_file_keeps_existing_working_copy(tmp_path: Path, recipes_file: Path) -> None:
    data_file = tmp_path / "data" / "recipes.json"
    data_file.parent.mkdir()
    data_file.write_text("[]", encoding="utf-8")

    ensure_data_file(data_file, seed_file=recipes_file)

    assert data_file.read_text(encoding="utf-8") == "[]"


def test_add_recipe_command_writes_working_copy_not_seed(isolated_data_file: Path) -> None:
    seed_before = SEED_FILE.read_text(encoding="utf-8")
    answers = "Test Toast\nbread\n1 slice\n\n5\n100\nToast it\n\n0\n"

    result = CliRunner().invoke(app, ["add-recipe"], input=answers)

    assert result.exit_code == 0
    assert "Test Toast" in [recipe.name for recipe in load_recipes(isolated_data_file)]
    assert SEED_FILE.read_text(encoding="utf-8") == seed_before

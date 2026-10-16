import json
from pathlib import Path

import pytest

from meal_planner.logic import create_recipe
from meal_planner.recipes import Recipe, add_recipe, load_recipes


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

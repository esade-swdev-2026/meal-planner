import random

import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.recipes import Recipe
from meal_planner.surprise import choose_surprise_meal

runner = CliRunner()


@pytest.fixture
def toast() -> Recipe:
    return Recipe("Toast", {"bread": "2 slices"}, 5, 250, ["Toast the bread"])


@pytest.fixture
def salad() -> Recipe:
    return Recipe("Salad", {"lettuce": "1"}, 10, 200, ["Mix everything"])


def test_surprise_meal_comes_from_the_matching_recipes(toast: Recipe, salad: Recipe) -> None:
    meal = choose_surprise_meal([toast, salad], random.Random(42))

    assert meal in [toast, salad]


def test_surprise_meal_with_one_option_returns_it(toast: Recipe) -> None:
    assert choose_surprise_meal([toast]) == toast


def test_surprise_meal_without_options_raises_error() -> None:
    with pytest.raises(ValueError):
        choose_surprise_meal([])


def test_cli_surprise_me_suggests_a_cookable_recipe() -> None:
    answer = "bread, tomatoes, garlic, olive oil, salt\n"

    result = runner.invoke(app, ["surprise-me"], input=answer)

    assert result.exit_code == 0
    assert "Today's suggestion: Pan con Tomate" in result.stdout


def test_cli_surprise_me_without_matching_recipes() -> None:
    result = runner.invoke(app, ["surprise-me"], input="water\n")

    assert result.exit_code == 0
    assert "No recipes can be made with those ingredients." in result.stdout

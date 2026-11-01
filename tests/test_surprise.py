import random

import pytest

from meal_planner.recipes import Recipe
from meal_planner.surprise import choose_surprise_meal


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

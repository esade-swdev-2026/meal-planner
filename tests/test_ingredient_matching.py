import pytest

from meal_planner.ingredient_matching import (
    find_cookable_recipes,
    normalize_ingredients,
)
from meal_planner.recipes import Recipe


@pytest.fixture
def toast() -> Recipe:
    return Recipe("Toast", {"bread": "2 slices"}, 5, 250, ["Toast the bread"])


@pytest.fixture
def pasta() -> Recipe:
    return Recipe(
        "Pasta",
        {"pasta": "200 g", "tomato sauce": "150 g"},
        20,
        650,
        ["Boil"],
    )


def test_normalize_ingredients_trims_lowercases_and_drops_blanks() -> None:
    assert normalize_ingredients([" Tomatoes ", "", "PASTA"]) == {"tomatoes", "pasta"}


def test_cookable_recipes_need_every_ingredient(toast: Recipe, pasta: Recipe) -> None:
    result = find_cookable_recipes([toast, pasta], ["pasta", "tomato sauce"])

    assert result == [pasta]


def test_cookable_recipes_ignore_case_and_spaces(pasta: Recipe) -> None:
    result = find_cookable_recipes([pasta], [" Pasta ", "TOMATO SAUCE"])

    assert result == [pasta]


def test_missing_one_ingredient_means_not_cookable(pasta: Recipe) -> None:
    assert find_cookable_recipes([pasta], ["pasta"]) == []


def test_recipe_without_ingredients_is_never_cookable() -> None:
    empty = Recipe("Air", {}, 1, 1, ["Breathe"])

    assert find_cookable_recipes([empty], ["pasta"]) == []

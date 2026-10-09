import pytest
from typer.testing import CliRunner

from meal_planner.cli import (
    Recipe,
    app,
    filter_by_calories,
    filter_by_ingredient,
    filter_by_time,
)

runner = CliRunner()


# CLI tests: check the commands and their output.


def test_show() -> None:
    result = runner.invoke(app, ["show"])

    assert result.exit_code == 0
    assert "Pasta with Tomato" in result.stdout
    assert "Avocado Toast" in result.stdout
    assert "Calories" in result.stdout


def test_cli_filter_by_ingredient() -> None:
    result = runner.invoke(
        app,
        ["filter-meals"],
        input="1\navocado\n",
    )

    assert result.exit_code == 0
    assert "Avocado Toast" in result.stdout


# Shared data for the pure-function tests.


@pytest.fixture
def sample_recipes() -> list[Recipe]:
    return [
        Recipe(
            name="Toast",
            ingredients={"bread": "2 slices"},
            cooking_time=10,
            calories=300,
            steps=["Toast the bread"],
        ),
        Recipe(
            name="Pasta",
            ingredients={"pasta": "200 g"},
            cooking_time=30,
            calories=600,
            steps=["Boil the pasta"],
        ),
    ]


# Ingredient filtering tests.


def test_ingredient_filter_on_empty_list() -> None:
    assert filter_by_ingredient([], "bread") == []


def test_ingredient_filter_returns_matching_recipe(
    sample_recipes: list[Recipe],
) -> None:
    result = filter_by_ingredient(sample_recipes, "bread")

    assert result == [sample_recipes[0]]


def test_missing_ingredient_returns_no_recipes(
    sample_recipes: list[Recipe],
) -> None:
    result = filter_by_ingredient(sample_recipes, "chicken")

    assert result == []


def test_ingredient_filter_ignores_input_case(
    sample_recipes: list[Recipe],
) -> None:
    result = filter_by_ingredient(sample_recipes, "BREAD")

    assert result == [sample_recipes[0]]


# Cooking-time filtering tests.


def test_time_filter_on_empty_list() -> None:
    assert filter_by_time([], 20) == []


@pytest.mark.parametrize(
    ("maximum", "expected_names"),
    [
        (0, []),
        (9, []),
        (10, ["Toast"]),
        (20, ["Toast"]),
        (30, ["Toast", "Pasta"]),
    ],
)
def test_time_filter_respects_limit(
    sample_recipes: list[Recipe],
    maximum: int,
    expected_names: list[str],
) -> None:
    result = filter_by_time(sample_recipes, maximum)

    assert [recipe.name for recipe in result] == expected_names


# Calorie filtering tests.


def test_calorie_filter_on_empty_list() -> None:
    assert filter_by_calories([], 400) == []


@pytest.mark.parametrize(
    ("maximum", "expected_names"),
    [
        (0, []),
        (299, []),
        (300, ["Toast"]),
        (400, ["Toast"]),
        (600, ["Toast", "Pasta"]),
    ],
)
def test_calorie_filter_respects_limit(
    sample_recipes: list[Recipe],
    maximum: int,
    expected_names: list[str],
) -> None:
    result = filter_by_calories(sample_recipes, maximum)

    assert [recipe.name for recipe in result] == expected_names

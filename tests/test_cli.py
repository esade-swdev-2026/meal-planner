import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.logic import (
    filter_by_calories,
    filter_by_ingredient,
    filter_by_time,
    find_fastest_recipe,
    find_recipe_by_name,
)
from meal_planner.recipes import SEED_FILE, Recipe, load_recipes
from meal_planner.shopping_list import build_shopping_list

runner = CliRunner()


@pytest.mark.parametrize(
    ("recipes", "expected_count"),
    [
        (
            [
                Recipe("Recipe A", {"bread": "1 slice"}, 5, 100, ["Toast"]),
                Recipe("Recipe B", {"eggs": "2"}, 5, 200, ["Fry"]),
            ],
            2,
        ),
        ([], 0),
    ],
)
def test_count_recipes(
    monkeypatch: pytest.MonkeyPatch,
    recipes: list[Recipe],
    expected_count: int,
) -> None:
    monkeypatch.setattr(
        "meal_planner.cli.load_recipes_or_exit",
        lambda: recipes,
    )

    result = runner.invoke(app, ["count-recipes"])

    assert result.exit_code == 0
    assert result.stdout.strip() == f"Total recipes: {expected_count}"


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


def test_fastest_meal(
    sample_recipes: list[Recipe],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipes = [sample_recipes[1], sample_recipes[0]]
    monkeypatch.setattr(
        "meal_planner.cli.load_recipes_or_exit",
        lambda: recipes,
    )

    result = runner.invoke(app, ["fastest-meal"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "Toast (10 min)"


def test_find_fastest_recipe_returns_none_for_empty_list() -> None:
    assert find_fastest_recipe([]) is None


def test_find_fastest_recipe_returns_first_on_tie(
    sample_recipes: list[Recipe],
) -> None:
    first = sample_recipes[0]
    twin = Recipe("Twin", first.ingredients, first.cooking_time, first.calories, first.steps)

    assert find_fastest_recipe([first, twin]) is first
    assert find_fastest_recipe([twin, first]) is twin


def test_fastest_meal_with_no_recipes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [])

    result = runner.invoke(app, ["fastest-meal"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "No recipes available."


@pytest.mark.parametrize(
    ("search", "expected"),
    [
        (" Eggs ", ["Omelette"]),
        ("egg", ["Omelette"]),
        ("tomato", ["Pasta"]),
        ("chicken", ["Chicken Salad"]),
        ("olive oil", ["Pasta", "Chicken Salad"]),
        ("oil", ["Pasta", "Chicken Salad"]),
        ("pea", []),
        ("   ", []),
    ],
)
def test_ingredient_search_matches_the_start_of_a_word(search: str, expected: list[str]) -> None:
    recipes = [
        Recipe("Omelette", {"eggs": "3"}, 10, 300, ["Fry"]),
        Recipe("Pasta", {"cherry tomatoes": "200 g", "olive oil": "10 ml"}, 15, 500, ["Boil"]),
        Recipe("Chicken Salad", {"chicken breast": "150 g", "olive oil": "5 ml"}, 20, 400, ["Mix"]),
        Recipe("Hummus", {"chickpeas": "400 g"}, 10, 350, ["Blend"]),
    ]

    found = filter_by_ingredient(recipes, search)

    assert [recipe.name for recipe in found] == expected


def test_ingredient_search_ignores_case_of_saved_names() -> None:
    recipes = [Recipe("Chicken Salad", {"Chicken Breast": "150 g"}, 20, 400, ["Mix"])]

    found = filter_by_ingredient(recipes, "chicken")

    assert [recipe.name for recipe in found] == ["Chicken Salad"]


def test_show_with_no_recipes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [])

    result = runner.invoke(app, ["show"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "No recipes available."


def test_weekly_plan_with_no_recipes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [])

    result = runner.invoke(app, ["weekly-plan"])

    assert result.exit_code == 1
    assert "No recipes are available." in result.output
    assert "CREATE YOUR WEEKLY PLAN" not in result.output


def test_help_describes_every_command_without_completion_options() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Suggest a random recipe" in result.stdout
    assert "--install-completion" not in result.stdout


@pytest.fixture
def two_recipes() -> list[Recipe]:
    return [
        Recipe(
            "Pan con Tomate", {"bread": "2 slices", "tomatoes": "120 g"}, 5, 250, ["Toast", "Rub"]
        ),
        Recipe("Baked Potato", {"potatoes": "300 g"}, 60, 300, ["Wash", "Bake"], 200),
    ]


def test_find_recipe_by_name_ignores_case_and_spaces(two_recipes: list[Recipe]) -> None:
    found = find_recipe_by_name(two_recipes, "  pan con TOMATE ")

    assert found is two_recipes[0]


def test_find_recipe_by_name_returns_none_when_missing(two_recipes: list[Recipe]) -> None:
    assert find_recipe_by_name(two_recipes, "Paella") is None


def test_recipe_by_name_shows_ingredients_and_numbered_steps(
    two_recipes: list[Recipe], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: two_recipes)

    result = runner.invoke(app, ["recipe", "baked potato"])

    assert result.exit_code == 0
    assert "BAKED POTATO" in result.stdout
    assert "Oven temperature: 200°C" in result.stdout
    assert "- potatoes: 300 g" in result.stdout
    assert "1. Wash\n2. Bake" in result.stdout


def test_recipe_with_an_unknown_name_is_an_error(
    two_recipes: list[Recipe], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: two_recipes)

    result = runner.invoke(app, ["recipe", "Paella"])

    assert result.exit_code == 1
    assert "Error: no recipe called 'Paella'" in result.output


def test_recipe_without_a_name_lets_you_choose_from_the_list(
    two_recipes: list[Recipe], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: two_recipes)

    result = runner.invoke(app, ["recipe"], input="9\n1\n")

    assert result.exit_code == 0
    assert "2. Baked Potato" in result.stdout
    assert "Please choose one of the displayed meal numbers." in result.stdout
    assert "PAN CON TOMATE" in result.stdout
    assert "1. Toast\n2. Rub" in result.stdout


def test_recipe_with_no_recipes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [])

    result = runner.invoke(app, ["recipe"])

    assert result.exit_code == 0
    assert result.stdout.strip() == "No recipes available."


def test_shipped_recipes_give_one_total_for_shared_vegetables() -> None:
    shopping_list = build_shopping_list(load_recipes(SEED_FILE))

    for ingredient in ("tomatoes", "potatoes", "onion"):
        assert "+" not in shopping_list[ingredient]

import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.recipes import Recipe
from meal_planner.shopping_list import build_shopping_list, combine_quantities

runner = CliRunner()


@pytest.fixture
def toast() -> Recipe:
    return Recipe("Toast", {"bread": "2 slices", "olive oil": "10 ml"}, 5, 250, ["Toast"])


@pytest.fixture
def pasta() -> Recipe:
    return Recipe("Pasta", {"pasta": "200 g", "olive oil": "15 ml"}, 20, 650, ["Boil"])


def test_quantities_with_the_same_unit_are_added() -> None:
    assert combine_quantities(["200 g", "150 g"]) == "350 g"


def test_quantities_without_a_unit_are_added() -> None:
    assert combine_quantities(["2", "3"]) == "5"


def test_quantities_with_different_units_are_listed() -> None:
    assert combine_quantities(["1 clove", "3 cloves"]) == "1 clove + 3 cloves"


def test_extra_spaces_do_not_stop_quantities_being_added() -> None:
    assert combine_quantities(["200  g", " 150 g "]) == "350 g"


def test_different_weight_units_are_not_added() -> None:
    assert combine_quantities(["1 kg", "500 g"]) == "1 kg + 500 g"


def test_empty_quantity_is_listed() -> None:
    assert combine_quantities(["", "2"]) == " + 2"


def test_quantities_that_are_not_whole_numbers_are_listed() -> None:
    assert combine_quantities(["1/2", "1"]) == "1/2 + 1"


def test_counted_items_with_a_word_unit_are_listed() -> None:
    assert combine_quantities(["1 clove", "1 clove"]) == "1 clove + 1 clove"


def test_single_quantity_is_kept_as_it_is() -> None:
    assert combine_quantities(["1/2"]) == "1/2"


def test_shopping_list_combines_shared_ingredients(toast: Recipe, pasta: Recipe) -> None:
    shopping_list = build_shopping_list([toast, pasta])

    assert shopping_list == {
        "bread": "2 slices",
        "olive oil": "25 ml",
        "pasta": "200 g",
    }


def test_meal_planned_twice_counts_twice(toast: Recipe) -> None:
    assert build_shopping_list([toast, toast])["olive oil"] == "20 ml"


def test_shopping_list_is_sorted_by_ingredient(toast: Recipe, pasta: Recipe) -> None:
    assert list(build_shopping_list([pasta, toast])) == ["bread", "olive oil", "pasta"]


def test_empty_plan_gives_empty_shopping_list() -> None:
    assert build_shopping_list([]) == {}


def test_cli_weekly_plan_shows_the_shopping_list(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    calories = "500\n"
    minutes_for_each_day = "10\n" * 7
    keep_the_plan = "n\n"

    result = runner.invoke(
        app, ["weekly-plan"], input=calories + minutes_for_each_day + keep_the_plan
    )

    assert result.exit_code == 0
    assert "SHOPPING LIST" in result.stdout
    assert "- bread: 2 slices + 2 slices" in result.stdout
    assert "- olive oil: 70 ml" in result.stdout

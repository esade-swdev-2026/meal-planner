import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.recipes import Recipe
from meal_planner.shopping_list import (
    build_shopping_list,
    combine_quantities,
    parse_quantity,
    subtract_owned_ingredients,
)

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
    nothing_owned = "n\n"

    result = runner.invoke(
        app,
        ["weekly-plan"],
        input=calories + minutes_for_each_day + keep_the_plan + nothing_owned,
    )

    assert result.exit_code == 0
    assert "SHOPPING LIST" in result.stdout
    assert "- bread: 2 slices + 2 slices" in result.stdout
    assert "- olive oil: 70 ml" in result.stdout
    assert "STILL TO BUY" not in result.stdout


def test_parse_quantity_splits_number_and_unit() -> None:
    assert parse_quantity("200 g") == (200, "g")
    assert parse_quantity("2") == (2, "")


def test_parse_quantity_refuses_what_cannot_be_added() -> None:
    assert parse_quantity("1/2") is None
    assert parse_quantity("3 cloves") is None
    assert parse_quantity("") is None


def test_owned_amount_is_subtracted() -> None:
    still_to_buy = subtract_owned_ingredients({"pasta": "500 g"}, {"pasta": "200 g"})

    assert still_to_buy == {"pasta": "300 g"}


def test_plain_counts_are_subtracted() -> None:
    assert subtract_owned_ingredients({"eggs": "6"}, {"eggs": "2"}) == {"eggs": "4"}


def test_ingredient_fully_covered_is_left_out() -> None:
    still_to_buy = subtract_owned_ingredients(
        {"pasta": "500 g", "milk": "200 ml"},
        {"pasta": "500 g", "milk": "1000 ml"},
    )

    assert still_to_buy == {}


def test_ingredients_not_owned_stay_on_the_list() -> None:
    still_to_buy = subtract_owned_ingredients({"pasta": "500 g", "salt": "5 g"}, {"pasta": "200 g"})

    assert still_to_buy == {"pasta": "300 g", "salt": "5 g"}


def test_different_units_are_not_subtracted() -> None:
    still_to_buy = subtract_owned_ingredients({"flour": "500 g"}, {"flour": "1 kg"})

    assert still_to_buy == {"flour": "500 g"}


def test_quantities_that_cannot_be_compared_stay_as_they_were() -> None:
    still_to_buy = subtract_owned_ingredients({"garlic": "3 cloves"}, {"garlic": "1 clove"})

    assert still_to_buy == {"garlic": "3 cloves"}


def test_owned_names_ignore_case_and_spaces() -> None:
    still_to_buy = subtract_owned_ingredients({"olive oil": "70 ml"}, {" Olive Oil ": "50 ml"})

    assert still_to_buy == {"olive oil": "20 ml"}


def test_cli_weekly_plan_subtracts_what_the_user_has(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    calories = "500\n"
    minutes_for_each_day = "10\n" * 7
    keep_the_plan = "n\n"
    owned_olive_oil = "y\nolive oil\n50 ml\n\n"

    result = runner.invoke(
        app,
        ["weekly-plan"],
        input=calories + minutes_for_each_day + keep_the_plan + owned_olive_oil,
    )

    assert result.exit_code == 0
    still_to_buy = result.stdout.split("STILL TO BUY")[1]
    assert "- olive oil: 20 ml" in still_to_buy
    assert "- bread: 2 slices + 2 slices" in still_to_buy

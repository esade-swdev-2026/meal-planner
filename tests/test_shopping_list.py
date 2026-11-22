import pytest
from typer.testing import CliRunner

from meal_planner.cli import app
from meal_planner.recipes import Recipe
from meal_planner.shopping_list import (
    Quantity,
    build_shopping_list,
    can_subtract,
    combine_quantities,
    format_quantity,
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


def weekly_plan_answers(owned: str) -> str:
    calories = "500\n"
    minutes_for_each_day = "10\n" * 7
    keep_the_plan = "n\n"
    return calories + minutes_for_each_day + keep_the_plan + owned


def test_parse_quantity_rejects_mixed_quantities() -> None:
    assert parse_quantity("500 g + 1") is None


def test_parse_quantity_splits_number_and_unit() -> None:
    assert parse_quantity("200 g") == Quantity(200, "g")
    assert parse_quantity("2") == Quantity(2, "")


def test_parse_quantity_converts_kilograms_and_litres() -> None:
    assert parse_quantity("1 kg") == Quantity(1000, "g")
    assert parse_quantity("0.5 l") == Quantity(500, "ml")


def test_parse_quantity_makes_word_units_singular() -> None:
    assert parse_quantity("3 cloves") == Quantity(3, "clove")
    assert parse_quantity("1 clove") == Quantity(1, "clove")


def test_parse_quantity_refuses_what_cannot_be_read() -> None:
    assert parse_quantity("1/2") is None
    assert parse_quantity("") is None
    assert parse_quantity("-5 g") is None
    assert parse_quantity("some") is None


def test_format_quantity_writes_plural_word_units() -> None:
    assert format_quantity(Quantity(4, "slice")) == "4 slices"
    assert format_quantity(Quantity(1, "clove")) == "1 clove"
    assert format_quantity(Quantity(2, "large")) == "2 large"
    assert format_quantity(Quantity(1.5, "g")) == "1.5 g"


def test_quantities_with_the_same_unit_are_added() -> None:
    assert combine_quantities(["200 g", "150 g"]) == "350 g"


def test_quantities_without_a_unit_are_added() -> None:
    assert combine_quantities(["2", "3"]) == "5"


def test_extra_spaces_do_not_stop_quantities_being_added() -> None:
    assert combine_quantities(["200  g", " 150 g "]) == "350 g"


def test_kilograms_and_grams_are_added_after_conversion() -> None:
    assert combine_quantities(["1 kg", "500 g"]) == "1500 g"


def test_litres_and_millilitres_are_added_after_conversion() -> None:
    assert combine_quantities(["0.5 l", "250 ml"]) == "750 ml"


def test_same_word_units_are_added_in_singular_or_plural() -> None:
    assert combine_quantities(["1 clove", "3 cloves"]) == "4 cloves"
    assert combine_quantities(["2 slices", "2 slices"]) == "4 slices"


def test_quantities_with_different_units_are_listed() -> None:
    assert combine_quantities(["1", "500 g"]) == "1 + 500 g"


def test_quantities_that_cannot_be_read_are_listed() -> None:
    assert combine_quantities(["1/2", "1"]) == "1/2 + 1"
    assert combine_quantities(["", "2"]) == " + 2"


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
    assert build_shopping_list([toast, toast])["bread"] == "4 slices"


def test_shopping_list_is_sorted_by_ingredient(toast: Recipe, pasta: Recipe) -> None:
    assert list(build_shopping_list([pasta, toast])) == ["bread", "olive oil", "pasta"]


def test_empty_plan_gives_empty_shopping_list() -> None:
    assert build_shopping_list([]) == {}


@pytest.mark.parametrize(
    ("needed", "owned", "expected"),
    [
        ("500 g", "200 g", True),
        ("500 g", "1 kg", True),
        ("1000 ml", "0.5 l", True),
        ("4 slices", "1 slice", True),
        ("500 g", "3", False),
        ("70 ml", "1 can", False),
        ("1/2 + 1/2", "1", False),
        ("500 g", "", False),
    ],
)
def test_can_subtract_only_comparable_quantities(needed: str, owned: str, expected: bool) -> None:
    assert can_subtract(needed, owned) is expected


def test_owned_amount_is_subtracted() -> None:
    result = subtract_owned_ingredients({"pasta": "500 g"}, {"pasta": "200 g"})

    assert result.shopping_list == {"pasta": "300 g"}
    assert result.not_subtracted == {}


def test_owned_amount_in_other_unit_is_converted() -> None:
    result = subtract_owned_ingredients(
        {"pasta": "500 g", "milk": "1000 ml"},
        {"pasta": "1 kg", "milk": "0.5 l"},
    )

    assert result.shopping_list == {"milk": "500 ml"}


def test_word_units_are_subtracted() -> None:
    result = subtract_owned_ingredients(
        {"bread": "4 slices", "garlic": "3 cloves"},
        {"bread": "4 slices", "garlic": "1 clove"},
    )

    assert result.shopping_list == {"garlic": "2 cloves"}


def test_plain_counts_are_subtracted() -> None:
    result = subtract_owned_ingredients({"eggs": "6"}, {"eggs": "2"})

    assert result.shopping_list == {"eggs": "4"}


def test_ingredients_not_owned_stay_on_the_list() -> None:
    result = subtract_owned_ingredients({"pasta": "500 g", "salt": "5 g"}, {"pasta": "200 g"})

    assert result.shopping_list == {"pasta": "300 g", "salt": "5 g"}


def test_different_units_are_kept_and_reported() -> None:
    result = subtract_owned_ingredients({"tomatoes": "500 g"}, {"tomatoes": "3"})

    assert result.shopping_list == {"tomatoes": "500 g"}
    assert result.not_subtracted == {"tomatoes": "3"}


def test_quantities_that_cannot_be_read_are_kept_and_reported() -> None:
    result = subtract_owned_ingredients({"onion": "1/2"}, {"onion": "1"})

    assert result.shopping_list == {"onion": "1/2"}
    assert result.not_subtracted == {"onion": "1"}


def test_owned_names_ignore_case_and_spaces() -> None:
    result = subtract_owned_ingredients({"olive oil": "70 ml"}, {" Olive Oil ": "50 ml"})

    assert result.shopping_list == {"olive oil": "20 ml"}


def test_cli_weekly_plan_shows_the_shopping_list(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers("n\n"))

    assert result.exit_code == 0
    assert "SHOPPING LIST" in result.stdout
    assert "- bread: 14 slices" in result.stdout
    assert "- olive oil: 70 ml" in result.stdout
    assert "STILL TO BUY" not in result.stdout


def test_cli_weekly_plan_subtracts_what_the_user_has(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    owned = "y\nolive oil\n50 ml\nbread\n4 slices\n\n"

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers(owned))

    assert result.exit_code == 0
    still_to_buy = result.stdout.split("STILL TO BUY")[1]
    assert "- olive oil: 20 ml" in still_to_buy
    assert "- bread: 10 slices" in still_to_buy


def test_cli_weekly_plan_asks_again_for_a_quantity_in_the_wrong_unit(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    owned = "y\nolive oil\n1 can\n0.05 l\n\n"

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers(owned))

    assert result.exit_code == 0
    assert "'1 can' cannot be compared with 70 ml" in result.stdout
    still_to_buy = result.stdout.split("STILL TO BUY")[1]
    assert "- olive oil: 20 ml" in still_to_buy


def test_cli_weekly_plan_asks_again_for_an_ingredient_not_on_the_list(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    owned = "y\nmilk\nolive oil\n50 ml\n\n"

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers(owned))

    assert result.exit_code == 0
    assert "'milk' is not on your shopping list." in result.stdout
    assert "- olive oil: 20 ml" in result.stdout.split("STILL TO BUY")[1]


def test_cli_weekly_plan_skips_an_ingredient_with_an_empty_quantity(
    toast: Recipe, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [toast])
    owned = "y\nolive oil\n\nbread\n2 slices\n\n"

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers(owned))

    assert result.exit_code == 0
    still_to_buy = result.stdout.split("STILL TO BUY")[1]
    assert "- olive oil: 70 ml" in still_to_buy
    assert "- bread: 12 slices" in still_to_buy


def test_cli_weekly_plan_explains_a_quantity_that_cannot_be_subtracted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    guacamole = Recipe("Guacamole", {"onion": "1/2", "avocado": "2"}, 10, 250, ["Mash"])
    monkeypatch.setattr("meal_planner.cli.load_recipes_or_exit", lambda: [guacamole])
    owned = "y\nonion\navocado\n4\n\n"

    result = runner.invoke(app, ["weekly-plan"], input=weekly_plan_answers(owned))

    assert result.exit_code == 0
    assert "of onion, which cannot be subtracted" in result.stdout
    still_to_buy = result.stdout.split("STILL TO BUY")[1]
    assert "- avocado: 10" in still_to_buy

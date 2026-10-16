import pytest

from meal_planner.recipes import Recipe
from meal_planner.weekly_planner import (
    DAYS,
    create_weekly_plan,
    find_alternatives,
    find_suitable_recipes,
    replace_meal,
)


@pytest.fixture
def toast() -> Recipe:
    return Recipe("Toast", {"bread": "2 slices"}, 5, 250, ["Toast the bread"])


@pytest.fixture
def salad() -> Recipe:
    return Recipe("Salad", {"lettuce": "1"}, 10, 200, ["Mix everything"])


@pytest.fixture
def lasagne() -> Recipe:
    return Recipe("Lasagne", {"pasta": "250 g"}, 60, 800, ["Bake"], oven_temperature=180)


def test_suitable_recipes_respect_both_limits(
    toast: Recipe, salad: Recipe, lasagne: Recipe
) -> None:
    result = find_suitable_recipes([toast, salad, lasagne], 300, 5)

    assert result == [toast]


def test_suitable_recipes_include_exact_limits(toast: Recipe) -> None:
    assert find_suitable_recipes([toast], 250, 5) == [toast]


def test_no_suitable_recipes_when_limits_too_low(toast: Recipe, salad: Recipe) -> None:
    assert find_suitable_recipes([toast, salad], 100, 60) == []


def test_plan_has_one_meal_per_day(toast: Recipe, salad: Recipe) -> None:
    daily_options = [[toast, salad] for _ in DAYS]

    plan = create_weekly_plan(daily_options)

    assert len(plan) == len(DAYS)


def test_each_planned_meal_comes_from_that_days_options(
    toast: Recipe, salad: Recipe, lasagne: Recipe
) -> None:
    daily_options = [[toast], [salad], [lasagne], [toast], [salad], [lasagne], [toast]]

    plan = create_weekly_plan(daily_options)

    assert plan == [toast, salad, lasagne, toast, salad, lasagne, toast]


def test_plan_needs_options_for_all_seven_days(toast: Recipe) -> None:
    with pytest.raises(ValueError):
        create_weekly_plan([[toast], [toast]])


def test_plan_needs_at_least_one_option_each_day(toast: Recipe) -> None:
    daily_options = [[toast] for _ in DAYS]
    daily_options[3] = []

    with pytest.raises(ValueError):
        create_weekly_plan(daily_options)


def test_alternatives_exclude_current_meal(toast: Recipe, salad: Recipe) -> None:
    assert find_alternatives([toast, salad], toast) == [salad]


def test_no_alternatives_when_only_current_meal_fits(toast: Recipe) -> None:
    assert find_alternatives([toast], toast) == []


def test_replace_meal_changes_only_that_day(toast: Recipe, salad: Recipe) -> None:
    plan = [toast] * len(DAYS)

    updated_plan = replace_meal(plan, 2, salad)

    assert updated_plan[2] == salad
    assert updated_plan[:2] == [toast, toast]
    assert updated_plan[3:] == [toast] * 4
    assert plan == [toast] * len(DAYS)


def test_replace_meal_rejects_day_outside_week(toast: Recipe, salad: Recipe) -> None:
    with pytest.raises(ValueError):
        replace_meal([toast] * len(DAYS), len(DAYS), salad)

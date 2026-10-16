import random

from meal_planner.logic import filter_by_calories, filter_by_time
from meal_planner.recipes import Recipe

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def find_suitable_recipes(
    available_recipes: list[Recipe],
    maximum_calories: int,
    maximum_minutes: int,
) -> list[Recipe]:
    suitable_recipes = filter_by_calories(available_recipes, maximum_calories)

    return filter_by_time(suitable_recipes, maximum_minutes)


def create_weekly_plan(daily_options: list[list[Recipe]]) -> list[Recipe]:
    if len(daily_options) != len(DAYS):
        raise ValueError("Provide recipe options for all seven days.")

    if any(not options for options in daily_options):
        raise ValueError("Every day must have at least one suitable recipe.")

    plan: list[Recipe] = []

    for options in daily_options:
        plan.append(random.choice(options))

    return plan


def find_alternatives(
    suitable_recipes: list[Recipe],
    current_meal: Recipe,
) -> list[Recipe]:
    alternatives: list[Recipe] = []

    for recipe in suitable_recipes:
        if recipe.name != current_meal.name:
            alternatives.append(recipe)

    return alternatives


def replace_meal(
    plan: list[Recipe],
    day_index: int,
    replacement: Recipe,
) -> list[Recipe]:
    if not 0 <= day_index < len(plan):
        raise ValueError(f"Day number must be between 1 and {len(plan)}.")

    updated_plan = list(plan)
    updated_plan[day_index] = replacement

    return updated_plan

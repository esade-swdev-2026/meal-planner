"""Helper functions for planning one meal per day for a week."""

import random

import typer

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


def ask_positive_integer(message: str) -> int:
    while True:
        number = int(typer.prompt(message, type=int))

        if number > 0:
            return number

        typer.echo("Please enter a whole number greater than zero.")


def find_suitable_recipes(
    available_recipes: list[Recipe],
    maximum_calories: int,
    maximum_minutes: int,
) -> list[Recipe]:
    suitable_recipes = filter_by_calories(
        available_recipes,
        maximum_calories,
    )

    return filter_by_time(suitable_recipes, maximum_minutes)


def ask_daily_options(
    available_recipes: list[Recipe],
    maximum_calories: int,
) -> list[list[Recipe]]:
    calorie_matches = filter_by_calories(
        available_recipes,
        maximum_calories,
    )

    if not calorie_matches:
        raise ValueError(
            "No recipes fit that calorie limit. Run the command again with a higher limit."
        )

    daily_options: list[list[Recipe]] = []

    for day in DAYS:
        while True:
            maximum_minutes = ask_positive_integer(f"Maximum cooking time for {day}, in minutes")

            suitable_recipes = find_suitable_recipes(
                available_recipes,
                maximum_calories,
                maximum_minutes,
            )

            if suitable_recipes:
                daily_options.append(suitable_recipes)
                break

            typer.echo(f"No recipes fit both limits for {day}. Please enter a longer cooking time.")

    return daily_options


def create_weekly_plan(
    daily_options: list[list[Recipe]],
) -> list[Recipe]:
    if len(daily_options) != len(DAYS):
        raise ValueError("Provide recipe options for all seven days.")

    if any(not options for options in daily_options):
        raise ValueError("Every day must have at least one suitable recipe.")

    plan: list[Recipe] = []

    for options in daily_options:
        selected_recipe = random.choice(options)
        plan.append(selected_recipe)

    return plan


def display_weekly_plan(plan: list[Recipe]) -> None:
    typer.echo("")

    for number, (day, recipe) in enumerate(
        zip(DAYS, plan, strict=True),
        start=1,
    ):
        typer.echo(
            f"{number}. {day}: {recipe.name} "
            f"— {recipe.calories} calories, "
            f"{recipe.cooking_time} minutes"
        )


def find_alternatives(
    suitable_recipes: list[Recipe],
    current_meal: Recipe,
) -> list[Recipe]:
    # Recipe names are unique: add_recipe() refuses a name that already exists.
    alternatives: list[Recipe] = []

    for recipe in suitable_recipes:
        if recipe.name != current_meal.name:
            alternatives.append(recipe)

    return alternatives


def edit_weekly_plan(
    plan: list[Recipe],
    daily_options: list[list[Recipe]],
) -> list[Recipe]:
    updated_plan = list(plan)

    while typer.confirm("Would you like to change a day?", default=False):
        day_index = ask_day_index()

        alternatives = find_alternatives(
            daily_options[day_index],
            updated_plan[day_index],
        )

        if not alternatives:
            typer.echo(
                "There are no other recipes within this day's limits. The current meal will stay."
            )
            continue

        replacement = choose_replacement(alternatives)
        updated_plan[day_index] = replacement

        display_weekly_plan(updated_plan)

    return updated_plan


def ask_day_index() -> int:
    while True:
        day_number = ask_positive_integer("Which day would you like to change? (1-7)")

        if day_number <= len(DAYS):
            return day_number - 1

        typer.echo("Please choose a day from 1 to 7.")


def choose_replacement(alternatives: list[Recipe]) -> Recipe:
    typer.echo("\n1. Choose another random meal")
    typer.echo("2. Choose a meal from a list")

    while True:
        option = ask_positive_integer("Choose an option")

        if option == 1:
            return random.choice(alternatives)

        if option == 2:
            return choose_recipe_from_list(alternatives)

        typer.echo("Please choose 1 or 2.")


def choose_recipe_from_list(
    alternatives: list[Recipe],
) -> Recipe:
    typer.echo("\nAVAILABLE MEALS")

    for number, recipe in enumerate(alternatives, start=1):
        typer.echo(
            f"{number}. {recipe.name} — {recipe.calories} calories, {recipe.cooking_time} minutes"
        )

    while True:
        choice = ask_positive_integer("Choose a meal number")

        if choice <= len(alternatives):
            return alternatives[choice - 1]

        typer.echo("Please choose one of the displayed meal numbers.")

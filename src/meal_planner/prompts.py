import random

import typer

from meal_planner.logic import filter_by_calories
from meal_planner.recipes import Recipe
from meal_planner.weekly_planner import (
    DAYS,
    find_alternatives,
    find_suitable_recipes,
    replace_meal,
)

RANDOM_MEAL_OPTION = 1
LIST_MEAL_OPTION = 2


def ask_positive_integer(message: str) -> int:
    while True:
        number = int(typer.prompt(message, type=int))

        if number > 0:
            return number

        typer.echo("Please enter a whole number greater than zero.")


def ask_ingredients() -> dict[str, str]:
    typer.echo("Enter the ingredients. Leave the name empty to finish.")
    ingredients: dict[str, str] = {}

    while True:
        ingredient = typer.prompt("Ingredient", default="", show_default=False).strip().lower()
        if ingredient == "":
            return ingredients

        quantity = typer.prompt(f"Quantity of {ingredient} (e.g. 200 g)")
        ingredients[ingredient] = quantity


def ask_steps() -> list[str]:
    typer.echo("Enter the steps. Leave the step empty to finish.")
    steps: list[str] = []

    while True:
        step = typer.prompt(f"Step {len(steps) + 1}", default="", show_default=False).strip()
        if step == "":
            return steps

        steps.append(step)


def ask_oven_temperature() -> int | None:
    oven = int(typer.prompt("Oven temperature in °C (0 if no oven)", type=int, default=0))

    if oven == 0:
        return None

    return oven


def ask_daily_options(
    available_recipes: list[Recipe],
    maximum_calories: int,
) -> list[list[Recipe]]:
    if not filter_by_calories(available_recipes, maximum_calories):
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


def display_weekly_plan(plan: list[Recipe]) -> None:
    typer.echo("")

    for number, (day, recipe) in enumerate(zip(DAYS, plan, strict=True), start=1):
        typer.echo(
            f"{number}. {day}: {recipe.name} "
            f"— {recipe.calories} calories, "
            f"{recipe.cooking_time} minutes"
        )


def edit_weekly_plan(
    plan: list[Recipe],
    daily_options: list[list[Recipe]],
) -> list[Recipe]:
    while typer.confirm("Would you like to change a day?", default=False):
        day_index = ask_day_index()

        alternatives = find_alternatives(daily_options[day_index], plan[day_index])

        if not alternatives:
            typer.echo(
                "There are no other recipes within this day's limits. The current meal will stay."
            )
            continue

        replacement = choose_replacement(alternatives)
        plan = replace_meal(plan, day_index, replacement)

        display_weekly_plan(plan)

    return plan


def ask_day_index() -> int:
    while True:
        day_number = ask_positive_integer(f"Which day would you like to change? (1-{len(DAYS)})")

        if day_number <= len(DAYS):
            return day_number - 1

        typer.echo(f"Please choose a day from 1 to {len(DAYS)}.")


def choose_replacement(alternatives: list[Recipe]) -> Recipe:
    typer.echo(f"\n{RANDOM_MEAL_OPTION}. Choose another random meal")
    typer.echo(f"{LIST_MEAL_OPTION}. Choose a meal from a list")

    while True:
        option = ask_positive_integer("Choose an option")

        if option == RANDOM_MEAL_OPTION:
            return random.choice(alternatives)

        if option == LIST_MEAL_OPTION:
            return choose_recipe_from_list(alternatives)

        typer.echo(f"Please choose {RANDOM_MEAL_OPTION} or {LIST_MEAL_OPTION}.")


def choose_recipe_from_list(alternatives: list[Recipe]) -> Recipe:
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

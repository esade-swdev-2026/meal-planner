from typing import NoReturn

import typer

from meal_planner.logic import (
    create_recipe,
    filter_by_calories,
    filter_by_ingredient,
    filter_by_time,
)
from meal_planner.prompts import (
    ask_daily_options,
    ask_ingredients,
    ask_oven_temperature,
    ask_positive_integer,
    ask_steps,
    display_weekly_plan,
    edit_weekly_plan,
)
from meal_planner.recipes import Recipe, add_recipe, load_recipes
from meal_planner.weekly_planner import create_weekly_plan

app = typer.Typer(help="Meal planner command-line application.")


def exit_with_error(message: str) -> NoReturn:
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


def load_recipes_or_exit() -> list[Recipe]:
    try:
        return load_recipes()
    except OSError as error:
        exit_with_error(f"could not open the recipes file ({error.strerror}).")
    except ValueError as error:
        exit_with_error(f"the recipes file is not valid. {error}")


@app.command()
def show() -> None:
    """Show all available meals."""
    recipes = load_recipes_or_exit()

    for recipe in recipes:
        typer.echo(f"\n{recipe.name}")
        typer.echo("Ingredients:")

        for ingredient, quantity in recipe.ingredients.items():
            typer.echo(f"- {ingredient}: {quantity}")

        typer.echo(f"Cooking time: {recipe.cooking_time} minutes")
        typer.echo(f"Calories: {recipe.calories}")

        if recipe.oven_temperature is not None:
            typer.echo(f"Oven temperature: {recipe.oven_temperature}°C")


@app.command()
def filter_meals() -> None:
    """Filter meals by ingredient, cooking time or calories."""
    recipes = load_recipes_or_exit()

    typer.echo("\nFILTER MEALS")
    typer.echo("1. Filter by ingredient")
    typer.echo("2. Filter by cooking time")
    typer.echo("3. Filter by calories")

    option = typer.prompt("Choose an option")

    if option == "1":
        ingredient = typer.prompt("Enter an ingredient")
        found_recipes = filter_by_ingredient(recipes, ingredient)

    elif option == "2":
        max_time = ask_positive_integer("Maximum cooking time in minutes")
        found_recipes = filter_by_time(recipes, max_time)

    elif option == "3":
        max_calories = ask_positive_integer("Maximum calories")
        found_recipes = filter_by_calories(recipes, max_calories)

    else:
        exit_with_error(f"'{option}' is not a valid option. Choose 1, 2 or 3.")

    if not found_recipes:
        typer.echo("No recipes found.")
    else:
        typer.echo("\nRECIPES FOUND:")

        for recipe in found_recipes:
            typer.echo(f"- {recipe.name} ({recipe.cooking_time} min, {recipe.calories} calories)")


@app.command("add-recipe")
def add_recipe_command() -> None:
    """Add a new recipe and save it to the JSON file."""
    typer.echo("\nADD A NEW RECIPE")
    name = typer.prompt("Recipe name")
    ingredients = ask_ingredients()
    cooking_time = int(typer.prompt("Cooking time in minutes", type=int))
    calories = int(typer.prompt("Calories", type=int))
    steps = ask_steps()
    oven_temperature = ask_oven_temperature()

    try:
        recipe = create_recipe(
            name,
            ingredients,
            cooking_time,
            calories,
            steps,
            oven_temperature,
        )
        add_recipe(recipe)
    except ValueError as error:
        exit_with_error(str(error))
    except OSError as error:
        exit_with_error(f"could not save the recipe ({error.strerror}).")

    typer.echo(f"'{recipe.name}' was added to your recipes.")


@app.command()
def weekly_plan() -> None:
    """Create a weekly plan and optionally replace meals."""
    available_recipes = load_recipes_or_exit()

    typer.echo("\nCREATE YOUR WEEKLY PLAN")
    typer.echo("We will plan one meal per day.")
    typer.echo("The calorie maximum applies to each planned meal.")

    try:
        if not available_recipes:
            raise ValueError("No recipes are available.")

        maximum_calories = ask_positive_integer("Maximum calories per planned meal")
        daily_options = ask_daily_options(available_recipes, maximum_calories)

        plan = create_weekly_plan(daily_options)
        display_weekly_plan(plan)

        plan = edit_weekly_plan(plan, daily_options)

    except ValueError as error:
        exit_with_error(str(error))

    typer.echo("\nYOUR FINAL PLAN")
    display_weekly_plan(plan)


if __name__ == "__main__":
    app()

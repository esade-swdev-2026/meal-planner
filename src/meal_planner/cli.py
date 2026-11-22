from typing import NoReturn

import typer

from meal_planner.ingredient_matching import find_cookable_recipes
from meal_planner.logic import (
    add_recipe_to_list,
    create_recipe,
    filter_by_calories,
    filter_by_ingredient,
    filter_by_time,
    find_fastest_recipe,
)
from meal_planner.prompts import (
    ask_daily_options,
    ask_ingredients,
    ask_oven_temperature,
    ask_owned_ingredients,
    ask_positive_integer,
    ask_steps,
    display_not_subtracted,
    display_shopping_list,
    display_weekly_plan,
    edit_weekly_plan,
)
from meal_planner.recipes import DATA_FILE, Recipe, ensure_data_file, load_recipes, save_recipes
from meal_planner.shopping_list import build_shopping_list, subtract_owned_ingredients
from meal_planner.surprise import choose_surprise_meal
from meal_planner.weekly_planner import create_weekly_plan

app = typer.Typer(help="Meal planner command-line application.", add_completion=False)


def exit_with_error(message: str) -> NoReturn:
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(code=1)


def load_recipes_or_exit() -> list[Recipe]:
    try:
        return load_recipes(ensure_data_file(DATA_FILE))
    except OSError as error:
        exit_with_error(f"could not open the recipes file ({error.strerror}).")
    except ValueError as error:
        exit_with_error(f"the recipes file is not valid. {error}")


@app.command()
def show() -> None:
    """Show all available meals."""
    recipes = load_recipes_or_exit()

    if not recipes:
        typer.echo("No recipes available.")
        return

    for recipe in recipes:
        typer.echo(f"\n{recipe.name}")
        typer.echo("Ingredients:")

        for ingredient, quantity in recipe.ingredients.items():
            typer.echo(f"- {ingredient}: {quantity}")

        typer.echo(f"Cooking time: {recipe.cooking_time} minutes")
        typer.echo(f"Calories: {recipe.calories}")

        if recipe.oven_temperature is not None:
            typer.echo(f"Oven temperature: {recipe.oven_temperature}°C")


@app.command("count-recipes")
def count_recipes() -> None:
    """Show the total number of available recipes."""
    recipes = load_recipes_or_exit()
    typer.echo(f"Total recipes: {len(recipes)}")


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
        path = ensure_data_file(DATA_FILE)
        save_recipes(add_recipe_to_list(load_recipes(path), recipe), path)
    except ValueError as error:
        exit_with_error(str(error))
    except OSError as error:
        exit_with_error(f"could not save the recipe ({error.strerror}).")

    typer.echo(f"'{recipe.name}' was added to your recipes.")


@app.command()
def weekly_plan() -> None:
    """Create a weekly plan, optionally replace meals, and show the shopping list."""
    available_recipes = load_recipes_or_exit()

    if not available_recipes:
        exit_with_error("No recipes are available.")

    typer.echo("\nCREATE YOUR WEEKLY PLAN")
    typer.echo("We will plan one meal per day.")
    typer.echo("The calorie maximum applies to each planned meal.")

    try:
        maximum_calories = ask_positive_integer("Maximum calories per planned meal")
        daily_options = ask_daily_options(available_recipes, maximum_calories)

        plan = create_weekly_plan(daily_options)
        display_weekly_plan(plan)

        plan = edit_weekly_plan(plan, daily_options)

    except ValueError as error:
        exit_with_error(str(error))

    typer.echo("\nYOUR FINAL PLAN")
    display_weekly_plan(plan)
    shopping_list = build_shopping_list(plan)
    display_shopping_list(shopping_list)

    owned_ingredients = ask_owned_ingredients()

    if owned_ingredients:
        still_to_buy = subtract_owned_ingredients(shopping_list, owned_ingredients)
        display_shopping_list(still_to_buy.shopping_list, title="STILL TO BUY")
        display_not_subtracted(still_to_buy.not_subtracted)


@app.command()
def surprise_me() -> None:
    """Suggest a random recipe you can cook with the ingredients you have."""
    recipes = load_recipes_or_exit()
    typer.echo("\nSURPRISE ME")
    answer = typer.prompt("Ingredients you have (separated by commas)")
    cookable_recipes = find_cookable_recipes(recipes, answer.split(","))

    try:
        recipe = choose_surprise_meal(cookable_recipes)
    except ValueError as error:
        typer.echo(str(error))
        return

    typer.echo(f"\nToday's suggestion: {recipe.name}")
    typer.echo(f"Cooking time: {recipe.cooking_time} minutes")
    typer.echo(f"Calories: {recipe.calories}")


@app.command()
def fastest_meal() -> None:
    """Show the recipe with the shortest cooking time."""
    recipes = load_recipes_or_exit()
    recipe = find_fastest_recipe(recipes)

    if recipe is None:
        typer.echo("No recipes available.")
        return

    typer.echo(f"{recipe.name} ({recipe.cooking_time} min)")


if __name__ == "__main__":
    app()

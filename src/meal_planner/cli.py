"""Typer commands and general CLI behaviour."""

import typer

from meal_planner.logic import (
    filter_by_calories,
    filter_by_ingredient,
    filter_by_time,
)
from meal_planner.recipes import Recipe, add_recipe, load_recipes

app = typer.Typer(help="Meal planner command-line application.")


@app.command()
def greet(name: str, count: int = 1) -> None:
    if count < 1:
        typer.echo("count must be at least 1", err=True)
        raise typer.Exit(code=1)
    for _ in range(count):
        typer.echo(f"Hello, {name}!")


@app.command()
def bye(name: str) -> None:
    typer.echo(f"Goodbye, {name}.")


@app.command()
def show() -> None:
    """Show all available meals."""
    recipes = load_recipes()

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
    recipes = load_recipes()

    typer.echo("\nFILTER MEALS")
    typer.echo("1. Filter by ingredient")
    typer.echo("2. Filter by cooking time")
    typer.echo("3. Filter by calories")

    option = typer.prompt("Choose an option")

    if option == "1":
        ingredient = typer.prompt("Enter an ingredient")
        found_recipes = filter_by_ingredient(recipes, ingredient)

    elif option == "2":
        max_time = typer.prompt(
            "Maximum cooking time in minutes",
            type=int,
        )
        found_recipes = filter_by_time(recipes, max_time)

    elif option == "3":
        max_calories = typer.prompt(
            "Maximum calories",
            type=int,
        )
        found_recipes = filter_by_calories(recipes, max_calories)

    else:
        typer.echo("Invalid option.")
        return

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

    typer.echo("Enter the ingredients. Leave the name empty to finish.")
    ingredients: dict[str, str] = {}
    while True:
        ingredient = typer.prompt("Ingredient", default="", show_default=False).strip().lower()
        if ingredient == "":
            break
        quantity = typer.prompt(f"Quantity of {ingredient} (e.g. 200 g)")
        ingredients[ingredient] = quantity

    cooking_time = typer.prompt("Cooking time in minutes", type=int)
    calories = typer.prompt("Calories", type=int)

    typer.echo("Enter the steps. Leave the step empty to finish.")
    steps: list[str] = []
    while True:
        step = typer.prompt(f"Step {len(steps) + 1}", default="", show_default=False).strip()
        if step == "":
            break
        steps.append(step)

    oven = typer.prompt("Oven temperature in °C (0 if no oven)", type=int, default=0)
    oven_temperature = oven if oven > 0 else None

    if len(ingredients) == 0 or len(steps) == 0:
        typer.echo("A recipe needs at least one ingredient and one step.", err=True)
        raise typer.Exit(code=1)

    recipe = Recipe(name, ingredients, cooking_time, calories, steps, oven_temperature)

    try:
        add_recipe(recipe)
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"'{name}' was added to your recipes.")


if __name__ == "__main__":
    app()

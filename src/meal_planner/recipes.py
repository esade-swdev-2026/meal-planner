"""Storage of recipes: the Recipe class and loading recipes from JSON."""

import json
from pathlib import Path

# recipes.json lives in the same folder as this file
RECIPES_FILE = Path(__file__).parent / "recipes.json"


class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict[str, str],
        cooking_time: int,
        calories: int,
        steps: list[str],
        oven_temperature: int | None = None,
    ) -> None:
        self.name = name
        self.ingredients = ingredients
        self.cooking_time = cooking_time
        self.calories = calories
        self.steps = steps
        self.oven_temperature = oven_temperature


def load_recipes(path: Path = RECIPES_FILE) -> list[Recipe]:
    """Read the JSON file and turn each entry into a Recipe object."""
    with open(path, encoding="utf-8") as file:
        data = json.load(file)  # a list of dictionaries

    # Recipe(**item) passes each key of the dictionary as a keyword argument,
    # e.g. Recipe(name="Sole", ingredients={...}, cooking_time=15, ...)
    return [Recipe(**item) for item in data]


def save_recipes(recipes: list[Recipe], path: Path = RECIPES_FILE) -> None:
    """Write all the recipes back to the JSON file."""
    # vars(recipe) turns a Recipe object into a dictionary of its attributes
    data = [vars(recipe) for recipe in recipes]

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def add_recipe(recipe: Recipe, path: Path = RECIPES_FILE) -> None:
    """Add one recipe to the JSON file."""
    recipes = load_recipes(path)

    for existing in recipes:
        if existing.name.lower() == recipe.name.lower():
            raise ValueError(f"A recipe called '{recipe.name}' already exists.")

    recipes.append(recipe)
    save_recipes(recipes, path)

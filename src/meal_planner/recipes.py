import json
from pathlib import Path

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
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    try:
        return [Recipe(**item) for item in data]
    except TypeError as error:
        raise ValueError(
            f"{path.name} contains a recipe with missing or unknown fields."
        ) from error


def save_recipes(recipes: list[Recipe], path: Path = RECIPES_FILE) -> None:
    data = [vars(recipe) for recipe in recipes]

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def add_recipe(recipe: Recipe, path: Path = RECIPES_FILE) -> None:
    recipes = load_recipes(path)

    for existing in recipes:
        if existing.name.lower() == recipe.name.lower():
            raise ValueError(f"A recipe called '{recipe.name}' already exists.")

    recipes.append(recipe)
    save_recipes(recipes, path)

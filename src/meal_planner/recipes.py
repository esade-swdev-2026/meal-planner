import json
import shutil
from pathlib import Path

SEED_FILE = Path(__file__).parent / "recipes.json"

DATA_FILE = Path("data") / "recipes.json"


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


def load_recipes(path: Path = DATA_FILE) -> list[Recipe]:
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    try:
        return [Recipe(**item) for item in data]
    except TypeError as error:
        raise ValueError(
            f"{path.name} contains a recipe with missing or unknown fields."
        ) from error


def save_recipes(recipes: list[Recipe], path: Path = DATA_FILE) -> None:
    data = [vars(recipe) for recipe in recipes]

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def add_recipe(recipe: Recipe, path: Path = DATA_FILE) -> None:
    from meal_planner.logic import add_recipe_to_list

    recipes = load_recipes(path)
    updated_recipes = add_recipe_to_list(recipes, recipe)
    save_recipes(updated_recipes, path)


def ensure_data_file(data_file: Path = DATA_FILE, seed_file: Path = SEED_FILE) -> Path:
    """Create the working copy from the seed if it does not exist yet."""
    if not data_file.exists():
        data_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed_file, data_file)

    return data_file

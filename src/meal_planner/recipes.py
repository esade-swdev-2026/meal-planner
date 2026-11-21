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


def is_positive_whole_number(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def is_text_pairs(value: object) -> bool:
    return isinstance(value, dict) and all(
        isinstance(key, str) and isinstance(item, str) for key, item in value.items()
    )


def is_text_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def check_recipe_fields(item: dict[str, object]) -> None:
    name = item["name"]

    if not isinstance(name, str) or not name.strip():
        raise ValueError("a recipe has an empty name.")

    if not item["ingredients"]:
        raise ValueError(f"'{name}' needs at least one ingredient.")

    if not is_text_pairs(item["ingredients"]):
        raise ValueError(f'\'{name}\' must list its ingredients as "name": "quantity".')

    for field in ("cooking_time", "calories"):
        if not is_positive_whole_number(item[field]):
            readable_field = field.replace("_", " ")
            raise ValueError(f"'{name}' has a {readable_field} that is not a whole number above 0.")

    if not item["steps"]:
        raise ValueError(f"'{name}' needs at least one step.")

    if not is_text_list(item["steps"]):
        raise ValueError(f"'{name}' must list its steps as text.")

    oven_temperature = item.get("oven_temperature")

    if oven_temperature is not None and not is_positive_whole_number(oven_temperature):
        raise ValueError(f"'{name}' has an oven temperature that is not a whole number above 0.")


def load_recipes(path: Path = DATA_FILE) -> list[Recipe]:
    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a list of recipes.")

    recipes = []

    for item in data:
        try:
            recipe = Recipe(**item)
        except TypeError as error:
            raise ValueError(
                f"{path.name} contains a recipe with missing or unknown fields."
            ) from error

        check_recipe_fields(item)
        recipes.append(recipe)

    return recipes


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
    if not data_file.exists():
        data_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(seed_file, data_file)

    return data_file

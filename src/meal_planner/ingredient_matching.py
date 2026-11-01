from collections.abc import Iterable

from meal_planner.recipes import Recipe


def normalize_ingredients(ingredients: Iterable[str]) -> set[str]:
    return {name.strip().lower() for name in ingredients if name.strip()}


def find_cookable_recipes(
    recipes: list[Recipe],
    available_ingredients: Iterable[str],
) -> list[Recipe]:
    available = normalize_ingredients(available_ingredients)
    cookable_recipes: list[Recipe] = []

    for recipe in recipes:
        required = normalize_ingredients(recipe.ingredients)

        if required and required <= available:
            cookable_recipes.append(recipe)

    return cookable_recipes

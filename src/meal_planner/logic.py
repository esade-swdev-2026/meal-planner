"""Business logic on recipes: filtering by ingredient, cooking time or calories."""

from meal_planner.recipes import Recipe


def filter_by_ingredient(
    recipes: list[Recipe],
    ingredient: str,
) -> list[Recipe]:
    matching_recipes: list[Recipe] = []

    for recipe in recipes:
        if ingredient.lower() in recipe.ingredients:
            matching_recipes.append(recipe)

    return matching_recipes


def filter_by_time(
    recipes: list[Recipe],
    maximum: int,
) -> list[Recipe]:
    matching_recipes: list[Recipe] = []

    for recipe in recipes:
        if recipe.cooking_time <= maximum:
            matching_recipes.append(recipe)

    return matching_recipes


def filter_by_calories(
    recipes: list[Recipe],
    maximum: int,
) -> list[Recipe]:
    matching_recipes: list[Recipe] = []

    for recipe in recipes:
        if recipe.calories <= maximum:
            matching_recipes.append(recipe)

    return matching_recipes

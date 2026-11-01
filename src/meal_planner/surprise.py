import random

from meal_planner.recipes import Recipe


def choose_surprise_meal(
    matching_recipes: list[Recipe],
    rng: random.Random | None = None,
) -> Recipe:
    if not matching_recipes:
        raise ValueError("No recipes can be made with those ingredients.")

    chooser = rng if rng is not None else random.Random()

    return chooser.choice(matching_recipes)

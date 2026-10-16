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


def create_recipe(
    name: str,
    ingredients: dict[str, str],
    cooking_time: int,
    calories: int,
    steps: list[str],
    oven_temperature: int | None = None,
) -> Recipe:
    if name.strip() == "":
        raise ValueError("A recipe needs a name.")

    if len(ingredients) == 0:
        raise ValueError("A recipe needs at least one ingredient.")

    if len(steps) == 0:
        raise ValueError("A recipe needs at least one step.")

    if cooking_time <= 0:
        raise ValueError("The cooking time must be greater than zero.")

    if calories <= 0:
        raise ValueError("The calories must be greater than zero.")

    if oven_temperature is not None and oven_temperature <= 0:
        raise ValueError("The oven temperature must be greater than zero.")

    return Recipe(
        name=name.strip(),
        ingredients=ingredients,
        cooking_time=cooking_time,
        calories=calories,
        steps=steps,
        oven_temperature=oven_temperature,
    )

from meal_planner.recipes import Recipe

ADDABLE_UNITS = ["", "g", "kg", "ml", "l"]


def combine_quantities(quantities: list[str]) -> str:

    if len(quantities) == 1:
        return quantities[0]

    total = 0
    units = []

    for quantity in quantities:
        parts = quantity.split(" ", 1)
        number = parts[0]
        unit = parts[1] if len(parts) == 2 else ""

        if not number.isdigit() or unit not in ADDABLE_UNITS:
            return " + ".join(quantities)

        total += int(number)
        units.append(unit)

    if len(set(units)) != 1:
        return " + ".join(quantities)

    return f"{total} {units[0]}".strip()


def build_shopping_list(plan: list[Recipe]) -> dict[str, str]:

    quantities: dict[str, list[str]] = {}

    for recipe in plan:
        for ingredient, quantity in recipe.ingredients.items():
            if ingredient not in quantities:
                quantities[ingredient] = []
            quantities[ingredient].append(quantity)

    shopping_list: dict[str, str] = {}

    for ingredient in sorted(quantities):
        shopping_list[ingredient] = combine_quantities(quantities[ingredient])

    return shopping_list

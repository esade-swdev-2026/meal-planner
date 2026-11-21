from meal_planner.recipes import Recipe

# Units we can add up or subtract safely. "" means a plain count, like "2" eggs.
ADDABLE_UNITS = ["", "g", "kg", "ml", "l"]


def parse_quantity(quantity: str) -> tuple[int, str] | None:
    parts = quantity.split()  # "200  g" -> ["200", "g"], "2" -> ["2"]

    if not parts or not parts[0].isdigit():
        return None

    unit = " ".join(parts[1:])

    if unit not in ADDABLE_UNITS:
        return None

    return int(parts[0]), unit


def format_quantity(amount: int, unit: str) -> str:
    return f"{amount} {unit}".strip()


def combine_quantities(quantities: list[str]) -> str:
    if len(quantities) == 1:
        return quantities[0]

    total = 0
    units = []

    for quantity in quantities:
        parsed = parse_quantity(quantity)

        if parsed is None:
            return " + ".join(quantities)

        amount, unit = parsed
        total += amount
        units.append(unit)

    if len(set(units)) != 1:  # not all the same unit
        return " + ".join(quantities)

    return format_quantity(total, units[0])


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


def subtract_owned_ingredients(
    shopping_list: dict[str, str],
    owned_ingredients: dict[str, str],
) -> dict[str, str]:
    owned = {name.strip().lower(): quantity for name, quantity in owned_ingredients.items()}
    still_to_buy: dict[str, str] = {}

    for ingredient, needed_quantity in shopping_list.items():
        if ingredient not in owned:
            still_to_buy[ingredient] = needed_quantity
            continue

        needed = parse_quantity(needed_quantity)
        have = parse_quantity(owned[ingredient])

        if needed is None or have is None:
            still_to_buy[ingredient] = needed_quantity
            continue

        needed_amount, needed_unit = needed
        have_amount, have_unit = have

        if needed_unit != have_unit:
            still_to_buy[ingredient] = needed_quantity
            continue

        remaining = needed_amount - have_amount

        if remaining > 0:
            still_to_buy[ingredient] = format_quantity(remaining, needed_unit)

    return still_to_buy

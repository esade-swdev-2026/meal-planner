from meal_planner.recipes import Recipe

MEASURED_UNITS = {
    "g": ("g", 1),
    "kg": ("g", 1000),
    "ml": ("ml", 1),
    "l": ("ml", 1000),
}

PLURAL_UNITS = {
    "clove": "cloves",
    "slice": "slices",
    "cup": "cups",
    "piece": "pieces",
    "teaspoon": "teaspoons",
    "tablespoon": "tablespoons",
    "pinch": "pinches",
    "bunch": "bunches",
    "glass": "glasses",
    "can": "cans",
    "egg": "eggs",
}

SINGULAR_UNITS = {plural: singular for singular, plural in PLURAL_UNITS.items()}


def to_singular(unit: str) -> str:
    return SINGULAR_UNITS.get(unit, unit)


def parse_quantity(quantity: str) -> tuple[float, str] | None:
    parts = quantity.lower().split()

    if not parts or not parts[0].replace(".", "", 1).isdigit():
        return None

    amount = float(parts[0])
    unit = " ".join(parts[1:])

    if unit in MEASURED_UNITS:
        base_unit, factor = MEASURED_UNITS[unit]
        return amount * factor, base_unit

    return amount, to_singular(unit)


def format_quantity(amount: float, unit: str) -> str:
    number = str(int(amount)) if amount.is_integer() else str(round(amount, 2))

    unit = to_singular(unit)
    if amount != 1:
        unit = PLURAL_UNITS.get(unit, unit)

    return f"{number} {unit}".strip()


def combine_quantities(quantities: list[str]) -> str:
    if len(quantities) == 1:
        return quantities[0]

    total = 0.0
    units = []

    for quantity in quantities:
        parsed = parse_quantity(quantity)

        if parsed is None:
            return " + ".join(quantities)

        amount, unit = parsed
        total += amount
        units.append(unit)

    if len(set(units)) != 1:
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
) -> tuple[dict[str, str], dict[str, str]]:
    owned = {name.strip().lower(): quantity for name, quantity in owned_ingredients.items()}
    still_to_buy: dict[str, str] = {}
    not_subtracted: dict[str, str] = {}

    for ingredient, needed_quantity in shopping_list.items():
        if ingredient not in owned:
            still_to_buy[ingredient] = needed_quantity
            continue

        needed = parse_quantity(needed_quantity)
        have = parse_quantity(owned[ingredient])

        if needed is None or have is None or needed[1] != have[1]:
            still_to_buy[ingredient] = needed_quantity
            not_subtracted[ingredient] = owned[ingredient]
            continue

        needed_amount, unit = needed
        have_amount, _ = have
        remaining = needed_amount - have_amount

        if remaining > 0:
            still_to_buy[ingredient] = format_quantity(remaining, unit)

    return still_to_buy, not_subtracted

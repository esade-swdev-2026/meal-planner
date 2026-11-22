from dataclasses import dataclass

from meal_planner.recipes import Recipe


@dataclass(frozen=True)
class Quantity:
    amount: float
    unit: str


@dataclass(frozen=True)
class StillToBuy:
    shopping_list: dict[str, str]
    not_subtracted: dict[str, str]


MEASURED_UNITS = {
    "g": Quantity(1, "g"),
    "kg": Quantity(1000, "g"),
    "ml": Quantity(1, "ml"),
    "l": Quantity(1000, "ml"),
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


def parse_quantity(quantity: str) -> Quantity | None:
    parts = quantity.lower().split()

    if not parts or not parts[0].replace(".", "", 1).isdigit():
        return None

    amount = float(parts[0])
    unit = " ".join(parts[1:])

    if unit in MEASURED_UNITS:
        one_unit = MEASURED_UNITS[unit]
        return Quantity(amount * one_unit.amount, one_unit.unit)

    return Quantity(amount, to_singular(unit))


def format_quantity(quantity: Quantity) -> str:
    amount = quantity.amount
    number = str(int(amount)) if amount.is_integer() else str(round(amount, 2))

    unit = to_singular(quantity.unit)
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

        total += parsed.amount
        units.append(parsed.unit)

    if len(set(units)) != 1:
        return " + ".join(quantities)

    return format_quantity(Quantity(total, units[0]))


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
) -> StillToBuy:
    owned = {name.strip().lower(): quantity for name, quantity in owned_ingredients.items()}
    still_to_buy: dict[str, str] = {}
    not_subtracted: dict[str, str] = {}

    for ingredient, needed_quantity in shopping_list.items():
        if ingredient not in owned:
            still_to_buy[ingredient] = needed_quantity
            continue

        needed = parse_quantity(needed_quantity)
        have = parse_quantity(owned[ingredient])

        if needed is None or have is None or needed.unit != have.unit:
            still_to_buy[ingredient] = needed_quantity
            not_subtracted[ingredient] = owned[ingredient]
            continue

        remaining = needed.amount - have.amount

        if remaining > 0:
            still_to_buy[ingredient] = format_quantity(Quantity(remaining, needed.unit))

    return StillToBuy(shopping_list=still_to_buy, not_subtracted=not_subtracted)

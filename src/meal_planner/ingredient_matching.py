"""Match recipes to the ingredients you have."""

from collections.abc import Iterable


def normalize_ingredients(ingredients: Iterable[str]) -> set[str]:
    """Lowercase and trim ingredient names, dropping blank ones."""
    return {name.strip().lower() for name in ingredients if name.strip()}

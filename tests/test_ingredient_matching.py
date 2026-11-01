from meal_planner.ingredient_matching import normalize_ingredients


def test_normalize_ingredients_trims_lowercases_and_drops_blanks() -> None:
    assert normalize_ingredients([" Tomatoes ", "", "PASTA"]) == {"tomatoes", "pasta"}

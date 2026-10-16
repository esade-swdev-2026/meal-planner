# Meal Planner

A command-line app that helps you decide what to cook. It comes with a set of simple
recipes and lets you:

- **see** every recipe with its ingredients, cooking time and calories,
- **filter** recipes by ingredient, maximum cooking time or maximum calories,
- **add** your own recipes,
- **plan a week**: one meal per day, within a calorie limit and a cooking time
  you choose for each day. You can then swap any day's meal.

## Install

You need [uv](https://docs.astral.sh/uv/) and git. uv installs the right Python
version and all dependencies for you.

```bash
git clone git@github.com:esade-swdev-2026/meal-planner.git
cd meal-planner
uv sync
```

Check that it works:

```bash
uv run meal-planner --help
```

## Usage

### See all recipes

```bash
uv run meal-planner show
```

```
Pasta with Tomato
Ingredients:
- pasta: 200 g
- tomato sauce: 150 g
...
Cooking time: 20 minutes
Calories: 650
```

### Filter recipes

```bash
uv run meal-planner filter-meals
```

Choose `1` (ingredient), `2` (cooking time) or `3` (calories), then type the
value. Example session:

```
FILTER MEALS
1. Filter by ingredient
2. Filter by cooking time
3. Filter by calories
Choose an option: 1
Enter an ingredient: eggs

RECIPES FOUND:
- Cheesecake (50 min, 700 calories)
- Avocado Toast (10 min, 400 calories)
- Spanish Omelette (35 min, 450 calories)
...
```

Ingredient names are matched exactly, in the plural where it applies:
`eggs`, `tomatoes`, `potatoes`, `bananas`.

### Plan your week

```bash
uv run meal-planner weekly-plan
```

You enter one maximum for calories per meal, then a maximum cooking time for
each day. The app picks a random suitable recipe for every day:

```
Maximum calories per planned meal: 500
Maximum cooking time for Monday, in minutes: 20
...
Maximum cooking time for Sunday, in minutes: 60

1. Monday: Chicken Stir Fry — 450 calories, 20 minutes
2. Tuesday: Scrambled Eggs — 300 calories, 5 minutes
...
Would you like to change a day? [y/N]:
```

Answer `y` to replace a day's meal, either with another random recipe or by
choosing from a list of recipes that fit that day's limits. Answer `n` (or
press Enter) to finish and see your final plan.

### Add a recipe

```bash
uv run meal-planner add-recipe
```

The app asks for the name, the ingredients and their quantities, the cooking
time, the calories, the steps and the oven temperature (`0` if no oven). To
finish the list of ingredients or steps, press Enter on an empty line.

New recipes are saved to `src/meal_planner/recipes.json`. A recipe with a name
that already exists, no ingredients, no steps, or a cooking time or calorie
value of zero is refused with a message, and nothing is saved.

### Errors

Bad input never crashes the program: you get a message starting with `Error:`
and the exit code is 1. For example, choosing option `9` in `filter-meals`, or
a missing or broken `recipes.json`.

## Run the checks

These are the same checks the GitHub Actions workflow runs:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest
```

- `ruff check` looks for common mistakes and style problems.
- `ruff format --check` checks the code formatting.
- `mypy` checks the type hints.
- `pytest` runs the tests in `tests/`.

## Project structure

The code is split so that calculations are kept apart from reading files and
talking to the user:

```
src/meal_planner/
├── recipes.json       the recipe data
├── recipes.py         storage: the Recipe class, loading and saving recipes.json
├── logic.py           business logic: filtering recipes, creating a new recipe
├── weekly_planner.py  business logic: building and changing a weekly plan
├── prompts.py         asking the user questions and printing results
├── cli.py             the Typer commands, which connect everything
└── __main__.py        lets you run the app with `python -m meal_planner`
tests/
├── test_cli.py             filters and the show / filter-meals commands
├── test_recipes.py         creating and adding recipes
├── test_weekly_planner.py  building and changing a weekly plan
└── test_bad_input.py       clear errors for bad input and broken files
```

## Use of AI

We used an AI assistant (Claude, by Anthropic) during this project. We used it to:

- **Polish our functions and tests**: improve names and type hints, fix the
  errors reported by ruff and mypy, and add tests for edge cases and bad input.
- **Write the recipes**: the recipes in `recipes.json` were written with AI,
  based on common, simple versions of well-known dishes. Calories and cooking
  times are approximate values per serving.
- **Check the project against the course**: make sure the concepts from class
  (the `src/` layout, separating storage, business logic and the CLI, pure
  functions with tests, clear error messages) and all the submission
  requirements are applied.
- **Restructure the code and write this README**: split the program into the
  modules listed above, add the error handling, and draft this README.

The team reviewed every change, ran the program and the checks
(`ruff`, `mypy` and `pytest`) ourselves, and decided what went into the final
version.

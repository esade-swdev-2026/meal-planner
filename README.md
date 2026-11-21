# Meal Planner

A command-line app that helps you decide what to cook. It comes with a set of simple
recipes and lets you:

- **see** every recipe with its ingredients, cooking time and calories,
- **filter** recipes by ingredient, maximum cooking time or maximum calories,
- **add** your own recipes,
- **plan a week**: one meal per day, within a calorie limit and a cooking time
  you choose for each day. You can then swap any day's meal.
- **build a shopping list** and subtract ingredients you already have,
- **get a surprise meal** using ingredients available to you,
- **count** your saved recipes,
- **find the fastest meal** to cook.

## Install

You need [uv](https://docs.astral.sh/uv/) and git. uv installs the right Python
version and all dependencies for you.

```bash
git clone https://github.com/esade-swdev-2026/meal-planner.git
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

At the end, the app shows a shopping list based on your final plan. It adds
compatible quantities, including counts such as slices and cloves, and converts
kg to g and l to ml. For example:

```
SHOPPING LIST
- bread: 4 slices
- garlic: 4 cloves
- olive oil: 100 ml
...
```

You can then enter ingredients you already have. Leave the ingredient name empty
to finish. The app subtracts those quantities and shows what is still missing:

```
Do you already have some of these ingredients? [y/N]: y
...

Ingredient: olive oil
Quantity of olive oil (e.g. 200 g): 50 ml
Ingredient:

STILL TO BUY
- bread: 4 slices
- garlic: 4 cloves
- olive oil: 50 ml
...
```

Ingredients you have enough of are removed. If a quantity cannot be subtracted,
the app displays a warning and keeps the original amount on the list.

### Add a recipe

```bash
uv run meal-planner add-recipe
```

The app asks for the name, the ingredients and their quantities, the cooking
time, the calories, the steps and the oven temperature (`0` if no oven). To
finish the list of ingredients or steps, press Enter on an empty line.

New recipes are saved to `data/recipes.json`, in the folder where you run the
app. The first time the app runs, it creates that file as a copy of the recipes
that ship with the app (`src/meal_planner/recipes.json`), which is never changed.
`data/` is ignored by git, so your own recipes do not show up in `git status`.
Delete `data/` to start again from the original recipes.

A recipe with a name that already exists, no ingredients, no steps, or a cooking
time or calorie value of zero is refused with a message, and nothing is saved.

### Surprise me

Suggests a random recipe that you can cook with the ingredients you have.

```bash
uv run meal-planner surprise-me
```

The app asks for your ingredients. Type them separated by commas. A recipe is only
suggested if you have **all** of its ingredients, and the names must match the
recipe's ingredient names (for example `tomatoes`, not `tomato`).

This command checks ingredient names, not quantities: it does not check whether
you have enough of each ingredient.

```
SURPRISE ME
Ingredients you have (separated by commas): bread, tomatoes, garlic, olive oil, salt

Today's suggestion: Pan con Tomate
Cooking time: 5 minutes
Calories: 250
```

If no recipe can be made with your ingredients, the app tells you so.

### Count recipes

Shows how many recipes the app has, including the ones you added yourself.

```bash
uv run meal-planner count-recipes
```

```
Total recipes: 26
```

### Fastest meal

Shows the recipe with the shortest cooking time. If two recipes take the same time,
the one that comes first in the list is shown.

```bash
uv run meal-planner fastest-meal
```

```
Pan con Tomate (5 min)
```

### Errors

Handled input and file errors produce a clear message and exit code `1`.
For example, choosing option `9` in `filter-meals` prints:

```text
Error: '9' is not a valid option. Choose 1, 2 or 3.
```

Invalid JSON and recipe files with missing or unknown fields are also reported
with an error message.

## Run with Docker

### Run the published image

You can run the app without cloning the repository or building the image:

```bash
docker pull ghcr.io/esade-swdev-2026/meal-planner:32fe963
docker run --rm ghcr.io/esade-swdev-2026/meal-planner:32fe963 --help
```

If the package is private, first run `docker login ghcr.io` using a GitHub
account with access and a token with `read:packages` permission.

Use `-it` for commands that ask questions. Your recipes are kept in a named
volume, `meal-data`, so they survive when the container is removed:

```bash
docker run --rm -it -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:32fe963 add-recipe
docker run --rm -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:32fe963 show
docker run --rm -it -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:32fe963 weekly-plan
```

Always use the same volume name to access your saved recipes. Without the
volume, changes are lost when the container is removed.

### Build the image yourself

Alternatively, from the project folder:

```bash
docker build -t meal-planner .
docker run --rm meal-planner --help
docker run --rm -it -v meal-data:/app/data meal-planner weekly-plan
```

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
├── recipes.json          the starting recipes (copied to data/recipes.json)
├── recipes.py            the Recipe class, loading and saving recipes
├── logic.py              filtering recipes and creating new recipes
├── weekly_planner.py     building and changing a weekly plan
├── shopping_list.py      combining quantities and subtracting owned ingredients
├── ingredient_matching.py matching available ingredients to recipes
├── surprise.py           choosing a random cookable recipe
├── prompts.py            asking questions and printing results
├── cli.py                the Typer commands, which connect everything
└── __main__.py           runs the app with python -m meal_planner
tests/
├── conftest.py                  temporary recipe data during tests
├── test_cli.py                  command behaviour and recipe filters
├── test_recipes.py              creating and saving recipes
├── test_weekly_planner.py       building and changing weekly plans
├── test_shopping_list.py        quantities, subtraction and shopping-list output
├── test_ingredient_matching.py  matching available ingredients
├── test_surprise.py             random meal selection and surprise-me
└── test_bad_input.py            errors for bad input and broken files
```

## Use of AI

We decided the structure of the project ourselves. We used AI assistants (Claude,
by Anthropic, and ChatGPT, by OpenAI) as a help during the project. We used them to:

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
  modules listed above, add the error handling, and draft and fix this README.

We asked the assistants to explain things before using them, and we only kept what
we understood. The team reviewed every change, ran the program and the checks
(`ruff`, `mypy` and `pytest`) ourselves, and decided what went into the final
version.

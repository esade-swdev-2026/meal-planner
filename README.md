# Meal Planner

A command-line app that helps you decide what to cook. It comes with 26 simple recipes
and lets you:

- **see** every recipe, or one recipe with the steps to cook it,
- **filter** recipes by ingredient, maximum cooking time or maximum calories,
- **plan a week**: one meal per day within the limits you set, then swap any day,
- **get a shopping list** for the week, minus the ingredients you already have,
- **get a surprise**: a random recipe you can cook with what is in your kitchen,
- **add** your own recipes, **count** them and find the **fastest** one.

## Commands at a glance

| Command | What it does |
| --- | --- |
| `show` | Shows every recipe with its ingredients, cooking time and calories |
| `recipe [NAME]` | Shows one recipe with its numbered steps; without a name, lets you pick from a list |
| `filter-meals` | Finds recipes by ingredient, maximum cooking time or maximum calories |
| `weekly-plan` | Plans a week of meals, then shows the shopping list and what is still to buy |
| `surprise-me` | Suggests a random recipe you can cook with the ingredients you have |
| `add-recipe` | Adds your own recipe |
| `count-recipes` | Shows how many recipes there are |
| `fastest-meal` | Shows the recipe with the shortest cooking time |

Run any command with `uv run meal-planner <command>`, or with Docker (see
[Run with Docker](#run-with-docker)).

## Install

You need [uv](https://docs.astral.sh/uv/) and git. uv installs Python 3.13 and all
the dependencies for you.

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

### See one recipe and how to cook it

Give the recipe's name (capital letters do not matter), or leave it out to choose
from a numbered list:

```bash
uv run meal-planner recipe "pan con tomate"
uv run meal-planner recipe
```

```
PAN CON TOMATE
Cooking time: 5 minutes
Calories: 250

Ingredients:
- bread: 2 slices
- tomatoes: 120 g
- garlic: 1 clove
- olive oil: 10 ml
- salt: 1 g

Steps:
1. Toast the bread
2. Rub the garlic on the toast
3. Rub or grate the tomato over the bread
4. Add olive oil and salt
```

### Filter recipes

```bash
uv run meal-planner filter-meals
```

Choose `1` (ingredient), `2` (cooking time) or `3` (calories), then type the value:

```
FILTER MEALS
1. Filter by ingredient
2. Filter by cooking time
3. Filter by calories
Choose an option: 1
Enter an ingredient: egg

RECIPES FOUND:
- Cheesecake (50 min, 700 calories)
- Avocado Toast (10 min, 400 calories)
- Spanish Omelette (35 min, 450 calories)
...
```

The ingredient search ignores capital letters and extra spaces, and matches the
start of any word in an ingredient's name: `egg` finds recipes with `eggs`,
`chicken` finds `chicken breast`, and `tomato` finds `cherry tomatoes`. It does
not match the middle of a word, so `pea` does not find `chickpeas`.

### Plan your week

```bash
uv run meal-planner weekly-plan
```

**1. Set your limits.** Enter one maximum for calories per meal, then a maximum
cooking time for each day. The app picks a random recipe that fits each day:

```
Maximum calories per planned meal: 500
Maximum cooking time for Monday, in minutes: 20
...
Maximum cooking time for Sunday, in minutes: 60

1. Monday: Pancakes — 450 calories, 20 minutes
2. Tuesday: Caprese Salad — 400 calories, 10 minutes
3. Wednesday: Scrambled Eggs — 300 calories, 5 minutes
...
7. Sunday: Caprese Salad — 400 calories, 10 minutes
Would you like to change a day? [y/N]:
```

**2. Swap any day.** Answer `y`, choose the day, then either another random recipe
or one from a list of recipes that fit that day's limits. Answer `n` (or press
Enter) when you are happy with the plan.

**3. Get the shopping list.** The app lists every ingredient the week needs:

```
SHOPPING LIST
- avocado: 1
- basil: 15 g
- bread: 2 slices
- eggs: 8
- milk: 260 ml
- mozzarella: 375 g
- olive oil: 45 ml
- tomatoes: 600 g
...
```

Quantities of the same ingredient are added up when they use the same kind of
unit: kilograms become grams, litres become millilitres, and counted items
(`2 slices` and `1 slice`) or plain numbers (eggs) are added too. Quantities that
cannot be added, such as a fraction like `1/2` or `120 g` and `2` of the same
ingredient, are listed side by side, so the list never shows a total it is not
sure of.

**4. Subtract what you already have.** The app asks whether you already have some
of these ingredients. Type each ingredient and how much you have, and press Enter
on an empty name to finish. Every answer is checked straight away: an ingredient
that is not on the list, or a quantity in a unit that cannot be compared with the
list, is refused and asked again. An empty quantity skips that ingredient.

```
Do you already have some of these ingredients? [y/N]: y
Enter what you already have. Leave the name empty to finish.
Ingredient: milk shake
'milk shake' is not on your shopping list.
Ingredient: olive oil
How much olive oil do you have? The list needs 45 ml (empty to skip): 2 cups
'2 cups' cannot be compared with 45 ml. Use the same unit as the list.
How much olive oil do you have? The list needs 45 ml (empty to skip): 0.05 l
Ingredient:

STILL TO BUY
- avocado: 1
- basil: 15 g
- bread: 2 slices
- eggs: 8
...
```

Olive oil is no longer on the list: 0.05 l is 50 ml, which covers the 45 ml the
week needs.

### Surprise me

```bash
uv run meal-planner surprise-me
```

Type the ingredients you have, separated by commas. The app suggests a random
recipe for which you have **all** the ingredients. Here the names must match the
recipe's ingredient names exactly (for example `tomatoes`, not `tomato`).

This command checks ingredient names, not quantities: it does not check
whether you have enough of each ingredient.

```
SURPRISE ME
Ingredients you have (separated by commas): bread, tomatoes, garlic, olive oil, salt

Today's suggestion: Pan con Tomate
Cooking time: 5 minutes
Calories: 250
```

If no recipe can be made with your ingredients, the app tells you so.

### Add a recipe

```bash
uv run meal-planner add-recipe
```

The app asks for the name, the ingredients and their quantities, the cooking time,
the calories, the steps and the oven temperature (`0` if no oven). To finish the
list of ingredients or steps, press Enter on an empty line.

A recipe with a name that already exists, no ingredients, no steps, or a cooking
time or calorie value of zero is refused with a message, and nothing is saved.

### Count recipes and find the fastest one

```bash
uv run meal-planner count-recipes
uv run meal-planner fastest-meal
```

```
Total recipes: 26
Pan con Tomate (5 min)
```

`count-recipes` includes the recipes you added yourself. If two recipes have the
same, shortest cooking time, `fastest-meal` shows the one that comes first in the
list.

### Where your recipes are saved

The app reads and saves recipes in `data/recipes.json`, in the folder where you run
it. The first time you run a command, it creates that file as a copy of the 26
recipes that ship with the app (`src/meal_planner/recipes.json`). After that it only
uses the copy, so your own recipes are never overwritten, and a newer version of the
app's recipes is not copied in by itself. `data/` is ignored by git.

To start again from the app's current recipes, rename your working copy as a
backup. The next run creates a fresh copy:

```bash
mv data/recipes.json data/recipes.backup.json
```

### Errors

Invalid input is either explained and requested again, or reported with an error
message and exit code `1`, depending on the command. Examples include choosing
option `9` in `filter-meals`, requesting an unknown recipe, or invalid JSON.
If a value in the recipes file has the wrong type, the message identifies the
recipe and field:

```
Error: the recipes file is not valid. 'Toast' has a cooking time that is not a whole number above 0.
```

## Run with Docker

### Run the published image

Every merge to `main` and the `v1.0` tag are built and published by our CI to
GitHub Container Registry. You can run the app without cloning the repository or
building the image:

If the package is private, first run `docker login ghcr.io` using an account
and token authorized to read the package.

```bash
docker pull ghcr.io/esade-swdev-2026/meal-planner:v1.0
docker run --rm ghcr.io/esade-swdev-2026/meal-planner:v1.0 --help
```

Your recipes are kept in a named volume, `meal-data`, so they survive when the
container is removed. Commands that ask questions need `-it`:

```bash
docker run --rm -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:v1.0 count-recipes
docker run --rm -it -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:v1.0 add-recipe
docker run --rm -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:v1.0 count-recipes
```

The first `count-recipes` prints `Total recipes: 26`. After adding a recipe, a
brand-new container prints `Total recipes: 27`: the recipe was saved in the volume,
not in the container. To plan a week, or to see a recipe:

```bash
docker run --rm -it -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:v1.0 weekly-plan
docker run --rm -v meal-data:/app/data ghcr.io/esade-swdev-2026/meal-planner:v1.0 recipe "pan con tomate"
```

Always use the same volume name to reach your saved recipes. Without `-v`, changes
are lost when the container is removed. To delete your saved recipes and start
again from the app's recipes:

```bash
docker volume rm meal-data
```

### Build the image yourself

From the project folder:

```bash
docker build -t meal-planner .
docker run --rm meal-planner --help
docker run --rm -it -v meal-data:/app/data meal-planner weekly-plan
```

## Run the checks

These are the same checks our GitHub Actions workflow runs on every push:

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src tests && uv run pytest
```

- `ruff check` looks for common mistakes and style problems.
- `ruff format --check` checks the code formatting.
- `mypy` checks the type hints.
- `pytest` runs the tests in `tests/`.

The workflow then builds the Docker image and runs it with `--help`. When the checks
pass on `main` or on a `v*` tag, a second job publishes the image to GitHub Container
Registry.

## Project structure

The code is split so that calculations are kept apart from reading files and
talking to the user:

```
src/meal_planner/
├── recipes.json            the starting recipes (read only; copied to data/recipes.json)
├── recipes.py              storage: the Recipe dataclass, loading, checking and saving recipes
├── logic.py                business logic: searching, filtering and creating recipes
├── weekly_planner.py       business logic: building and changing a weekly plan
├── shopping_list.py        business logic: adding up quantities, subtracting what you have
├── ingredient_matching.py  business logic: which recipes you can cook with your ingredients
├── surprise.py             business logic: picking a random cookable recipe
├── prompts.py              asking the user questions and printing results
├── cli.py                  the Typer commands, which connect everything
└── __main__.py             lets you run the app with `python -m meal_planner`
tests/
├── conftest.py                  points the app to a temporary data file during tests
├── test_cli.py                  searching, filters, fastest meal, the recipe command and the CLI
├── test_recipes.py              creating, saving and loading recipes
├── test_weekly_planner.py       building and changing a weekly plan
├── test_shopping_list.py        quantities, the shopping list and what is still to buy
├── test_ingredient_matching.py  matching your ingredients to recipes
├── test_surprise.py             the surprise-me command
└── test_bad_input.py            clear errors for bad input and broken files
Dockerfile                  builds the image: dependencies first, runs as a non-root user
.dockerignore               keeps .venv, .git, caches and data/ out of the image
.github/workflows/check.yml the checks, the image build and the release job
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

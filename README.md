# app

> **First thing: rename `app` to your project.** It appears in this file, in
> `pyproject.toml` (`name`, `[project.scripts]`, `[tool.hatch.build.targets.wheel]`),
> in the folder `src/app/`, and in the imports under `tests/`. Session 5's lab walks
> you through it.

One or two sentences on what your program does and who it is for.

## Install

```
uv sync
```

This creates a virtual environment and installs everything, including the development
tools, from `uv.lock` — the committed file that pins exact versions so every teammate
and CI resolve the same ones. When you change a dependency in `pyproject.toml`, run
`uv lock` and commit the updated `uv.lock`; CI fails if the two disagree.

## Run

# Meal Planner

Meal Planner is a command-line application that allows users to view available meals and filter them based on different preferences such as ingredients, cooking time, and calories.

It is designed for users who want a simple way to explore meal options and decide what they could cook.

## Install

```bash
uv sync
```

This creates a virtual environment and installs everything, including the development tools, from `uv.lock`.

When you change a dependency in `pyproject.toml`, run:

```bash
uv lock
```

and commit the updated `uv.lock`.

## Run

To see the available commands:

```bash
uv run meal-planner --help
```

To view all meals:

```bash
uv run meal-planner show
```

To filter meals:

```bash
uv run meal-planner filter-meals
```

The filtering option allows users to search meals by ingredient, cooking time, or calories.

## Tests

To run the tests:

```bash
uv run pytest
```

The tests check that the main features of the application work correctly.

## Development checks

Before pushing changes, run:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests
uv run pytest
```

These checks verify the code style, formatting, types, and tests.

## Project structure

```text
src/meal_planner/
    cli.py
    __main__.py

tests/
    test_cli.py

pyproject.toml
uv.lock
README.md
```

- `cli.py` contains the Meal Planner commands and recipes.
- `__main__.py` starts the application.
- `tests/` contains the tests.
- `pyproject.toml` contains the project configuration and dependencies.
- `uv.lock` stores the exact dependency versions.

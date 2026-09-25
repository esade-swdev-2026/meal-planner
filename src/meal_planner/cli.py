import typer

app = typer.Typer(help="Meal planner command-line application.")


@app.command()
def greet(name: str, count: int = 1) -> None:
    if count < 1:
        typer.echo("count must be at least 1", err=True)
        raise typer.Exit(code=1)
    for _ in range(count):
        typer.echo(f"Hello, {name}!")


@app.command()
def bye(name: str) -> None:
    typer.echo(f"Goodbye, {name}.")


class Recipe:
    def __init__(
        self,
        name: str,
        ingredients: dict,
        cooking_time: int,
        calories: int,
        steps: list,
        oven_temperature: int | None = None,
    ) -> None:
        self.name = name
        self.ingredients = ingredients
        self.cooking_time = cooking_time
        self.calories = calories
        self.steps = steps
        self.oven_temperature = oven_temperature


pasta = Recipe(
    name="Pasta with Tomato",
    ingredients={
        "pasta": "200 g",
        "tomato sauce": "150 g",
        "parmesan": "40 g",
        "olive oil": "10 ml",
        "salt": "2 g",
    },
    cooking_time=20,
    calories=650,
    steps=[
        "Boil the pasta",
        "Heat the tomato sauce",
        "Mix the pasta with the sauce",
        "Add parmesan",
    ],
)


filet_mignon = Recipe(
    name="Filet Mignon",
    ingredients={
        "beef fillet": "200 g",
        "butter": "20 g",
        "garlic": "1 clove",
        "salt": "2 g",
        "pepper": "1 g",
    },
    cooking_time=20,
    calories=500,
    steps=[
        "Season the beef with salt and pepper",
        "Heat a pan",
        "Cook the beef on both sides",
        "Add butter and garlic",
        "Let the meat rest before serving",
    ],
)


sole = Recipe(
    name="Sole",
    ingredients={
        "sole": "250 g",
        "lemon": "1",
        "butter": "15 g",
        "parsley": "5 g",
        "salt": "2 g",
    },
    cooking_time=15,
    calories=300,
    steps=[
        "Season the sole",
        "Heat butter in a pan",
        "Cook the fish on both sides",
        "Add lemon and parsley",
    ],
)


cheesecake = Recipe(
    name="Cheesecake",
    ingredients={
        "cream cheese": "250 g",
        "biscuits": "100 g",
        "butter": "50 g",
        "sugar": "80 g",
        "eggs": "2",
    },
    cooking_time=50,
    calories=700,
    steps=[
        "Crush the biscuits",
        "Mix the biscuits with melted butter",
        "Mix cream cheese, sugar and eggs",
        "Pour the mixture over the biscuit base",
        "Bake the cheesecake",
    ],
    oven_temperature=180,
)


avocado_toast = Recipe(
    name="Avocado Toast",
    ingredients={
        "bread": "2 slices",
        "avocado": "1",
        "egg": "1",
        "salt": "1 g",
        "pepper": "1 g",
    },
    cooking_time=10,
    calories=400,
    steps=[
        "Toast the bread",
        "Mash the avocado",
        "Spread the avocado on the toast",
        "Cook the egg",
        "Place the egg on top",
    ],
)


recipes = [
    pasta,
    filet_mignon,
    sole,
    cheesecake,
    avocado_toast,
]


@app.command()
def show() -> None:
    """Show all available meals."""

    for recipe in recipes:
        typer.echo(f"\n{recipe.name}")
        typer.echo("Ingredients:")

        for ingredient, quantity in recipe.ingredients.items():
            typer.echo(f"- {ingredient}: {quantity}")

        typer.echo(f"Cooking time: {recipe.cooking_time} minutes")
        typer.echo(f"Calories: {recipe.calories}")

        if recipe.oven_temperature is not None:
            typer.echo(f"Oven temperature: {recipe.oven_temperature}°C")


@app.command()
def filter_meals() -> None:
    """Filter meals by ingredient, cooking time or calories."""

    typer.echo("\nFILTER MEALS")
    typer.echo("1. Filter by ingredient")
    typer.echo("2. Filter by cooking time")
    typer.echo("3. Filter by calories")

    option = typer.prompt("Choose an option")

    found_recipes = []

    if option == "1":
        ingredient = typer.prompt("Enter an ingredient").lower()

        for recipe in recipes:
            if ingredient in recipe.ingredients:
                found_recipes.append(recipe)

    elif option == "2":
        max_time = typer.prompt(
            "Maximum cooking time in minutes",
            type=int,
        )

        for recipe in recipes:
            if recipe.cooking_time <= max_time:
                found_recipes.append(recipe)

    elif option == "3":
        max_calories = typer.prompt(
            "Maximum calories",
            type=int,
        )

        for recipe in recipes:
            if recipe.calories <= max_calories:
                found_recipes.append(recipe)

    else:
        typer.echo("Invalid option.")
        return

    if len(found_recipes) == 0:
        typer.echo("No recipes found.")

    else:
        typer.echo("\nRECIPES FOUND:")

        for recipe in found_recipes:
            typer.echo(f"- {recipe.name} ({recipe.cooking_time} min, {recipe.calories} calories)")


if __name__ == "__main__":
    app()

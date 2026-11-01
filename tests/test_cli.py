from typer.testing import CliRunner

from meal_planner.cli import app

runner = CliRunner()


def test_show() -> None:
    result = runner.invoke(app, ["show"])

    assert result.exit_code == 0
    assert "Pasta with Tomato" in result.stdout
    assert "Avocado Toast" in result.stdout
    assert "Calories" in result.stdout


def test_filter_by_ingredient() -> None:
    result = runner.invoke(
        app,
        ["filter-meals"],
        input="1\navocado\n",
    )

    assert result.exit_code == 0
    assert "Avocado Toast" in result.stdout

def test_how_to_cook():
    result = runner.invoke(app, ["how-to-cook"], input="Pasta with Tomato\n")

    assert result.exit_code == 0
    assert "pasta" in result.output
    assert "Boil the pasta" in result.output
    assert "20" in result.output


def test_how_to_cook_invalid():
    result = runner.invoke(app, ["how-to-cook"], input="Pizza\n")

    assert result.exit_code == 0
    assert "Recipe not found." in result.output
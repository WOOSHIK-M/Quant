import click

from src.dashboard import DashBoard


@click.group()
def main():
    """Run group of CLI."""


@click.command()
@click.option("--dummy", type=str, default="", help="Dummy argument.")
def run(dummy: str) -> None:
    """Run."""
    DashBoard().run()


if __name__ == "__main__":
    main.add_command(run)

    main()

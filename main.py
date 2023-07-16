import click

from src.client import UpbitAccount


@click.group()
def main():
    """Run group of CLI."""


@click.command()
@click.option("--dummy", type=str, default="", help="Dummy argument.")
def run(dummy: str) -> None:
    """Run."""
    UpbitAccount


if __name__ == "__main__":
    main.add_command(run)

    main()

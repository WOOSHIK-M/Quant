import click

from src.dashboard import DashBoard


@click.group()
def main():
    """Run group of CLI."""


@click.command()
@click.option("--dashboard", is_flag=True, default=False, help="Use dashboard.")
def run(dashboard: bool) -> None:
    """Run."""
    if dashboard:
        DashBoard().run()


if __name__ == "__main__":
    main.add_command(run)

    main()

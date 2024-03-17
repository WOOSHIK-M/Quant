import click

from quant.data_miner import UpbitCandleMiner


@click.group()
def main() -> None:
    """Run group."""


@main.command()
def mining() -> None:
    """Always maintain the newest candle data.

    Notes:
        It will be integrated with dashboard by a single command.
    """
    UpbitCandleMiner().run()


if __name__ == "__main__":
    main.add_command(mining)

    main()

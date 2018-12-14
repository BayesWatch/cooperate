# -*- coding: utf-8 -*-

"""Console script for cooperate."""
import sys
import click
from cooperate import cooperate


@click.command()
@click.option("--doe", 'doe_path', type=str, required=False, default=None)
@click.option("--run", 'to_run', type=str, required=False, default=None)
def main(doe_path, to_run, args=None):
    """Console script for cooperate."""
    if doe_path is not None:
        cooperate.build_doe(doe_path)
    elif to_run is not None:
        cooperate.run_experiments(to_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

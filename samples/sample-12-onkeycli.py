import click

from pi0servo import click_common_opts, get_logger
from pi0servo.utils.onekeycli import OneKeyCli


@click.command()
@click_common_opts("0.0.1", use_h=False)
def main(ctx, debug):
    """Main."""
    __log = get_logger(__name__, debug)
    __log.debug("")

    app = None
    try:
        app = OneKeyCli(debug=debug)
        app.main()
    finally:
        if app:
            app.end()


if __name__ == "__main__":
    main()

import click

from pi0servo import CliBase, click_common_opts, get_logger


@click.command()
@click.option(
    "--history_file", "-h", type=str, default="/tmp/hist", show_default=True,
    help="history file"
)
@click_common_opts("0.0.1", use_h=False)
def main(ctx, history_file, debug):
    """Main."""
    __log = get_logger(__name__)
    __log.debug("history_file=%a", history_file)

    app = None
    try:
        app = CliBase("> ", history_file=history_file, debug=debug)
        app.main()
    finally:
        if app:
            app.end()


if __name__ == '__main__':
    main()

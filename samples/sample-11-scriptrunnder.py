import click

from pi0servo import ScriptRunner, click_common_opts, get_logger


@click.command()
@click.option(
    "--script_file", "-s", type=str, default="",
    help="script file"
)
@click_common_opts("0.0.1", use_h=False)
def main(ctx, script_file, debug):
    """Main."""
    __log = get_logger(__name__)
    __log.debug("script_file=%a", script_file)

    app = None
    try:
        app = ScriptRunner(script_file, debug=debug)
        app.main()
    finally:
        if app:
            app.end()


if __name__ == '__main__':
    main()

import click

from pi0servo import ScriptRunner, click_common_opts, get_logger


@click.command()
@click.option("--script_file", "-s", type=str, default="", help="script file")
@click_common_opts("0.0.1")
def main(ctx, script_file, debug):
    """Main."""
    command_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("command_name=%a", command_name)
    __log.debug("script_file=%a", script_file)

    app = None
    try:
        app = ScriptRunner(script_file, debug=debug)
        app.main()
    finally:
        if app:
            app.end()


if __name__ == "__main__":
    main()

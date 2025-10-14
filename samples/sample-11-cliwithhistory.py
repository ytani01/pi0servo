import click

from pi0servo import CliWithHistory, click_common_opts, get_logger


@click.command()
@click.option(
    "--history_file",
    "-f",
    type=str,
    default="/tmp/hist",
    show_default=True,
    help="History file",
)
@click_common_opts("0.0.1", use_h=False)
def main(ctx, history_file, debug):
    """Main."""
    command_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("command_name=%a", command_name)
    __log.debug("history_file=%a", history_file)

    app = None
    try:
        prompt_str = command_name + "> "
        app = CliWithHistory(prompt_str, history_file, debug=debug)
        app.main()

    finally:
        if app:
            app.end()


if __name__ == "__main__":
    main()

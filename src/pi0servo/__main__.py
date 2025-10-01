#
# (c) 2025 Yoichi Tanibayashi
#
"""__main__.py"""

import os

import click
import pigpio
from pyclickutils import click_common_opts

from . import __version__, get_logger
from .command.cmd_apicli import CmdApiCli
from .command.cmd_apiclient import CmdApiClient
from .command.cmd_apiserver import CmdApiServer
from .command.cmd_calib import CalibApp
from .command.cmd_servo import CmdServo
from .command.cmd_strcli import CmdStrCli
from .command.cmd_strclient import CmdStrClient
from .core.calibrable_servo import CalibrableServo


def get_pi(debug=False) -> pigpio.pi:
    """Initialize and return a pigpio.pi instance.
    If connection fails, log an error and return None.
    """
    __log = get_logger(__name__, debug)

    pi = pigpio.pi()
    if not pi.connected:
        __log.error("pigpio daemon not connected.")
        raise ConnectionError("pigpio daemon not connected.")
    return pi


def print_pins_error(ctx):
    """Print error message and help."""
    click.echo()
    click.echo(click.style("Error: Please specify GPIO pins.", fg="red"))
    click.echo()
    click.echo(f"{ctx.get_help()}")


@click.group()
@click_common_opts(click, __version__)
def cli(ctx, debug):
    """pi0servo CLI top."""
    cmd_name = ctx.info_name
    subcmd_name = ctx.invoked_subcommand

    ___log = get_logger(cmd_name, debug)

    ___log.debug("cmd_name=%s, subcmd_name=%s", cmd_name, subcmd_name)

    if subcmd_name is None:
        click.echo(ctx.get_help())


@cli.command()
@click.argument("pin", type=int, nargs=1)
@click.argument("pulse", type=str, nargs=1)
@click.option(
    "--wait-sec",
    "-s",
    "-w",
    type=float,
    default=0.8,
    show_default=True,
    help="wait sec",
)
@click_common_opts(click, __version__)
def servo(ctx, pin: int, pulse: int, wait_sec: float, debug: bool) -> None:
    """servo command."""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug('pin=%s, pulse="%s", wait_sec=%s', pin, pulse, wait_sec)

    pi = None
    app = None
    try:
        pi = get_pi(debug)
        app = CmdServo(pi, pin, pulse, wait_sec, debug=debug)
        app.main(ctx)

    except Exception as _e:
        __log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


@cli.command()
@click.argument("pin", type=int, nargs=1)
@click.option(
    "--conf_file",
    "-c",
    "-f",
    type=str,
    default=CalibrableServo.DEF_CONF_FILE,
    show_default=True,
    help="Config file",
)
@click_common_opts(click, __version__)
def calib(ctx, pin, conf_file, debug):
    """calibration tool

    * configuration search path:

        Current dir --> Home dir --> /etc
    """
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug("pin=%s,conf_file=%s", pin, conf_file)

    if not pin:
        print_pins_error(ctx)
        return

    pi = None
    app = None
    try:
        pi = get_pi(debug)
        app = CalibApp(pi, pin, conf_file, debug=debug)
        app.main()

    except (EOFError, KeyboardInterrupt):
        pass

    except Exception as _e:
        __log.error("%s: %s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


@cli.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--history_file",
    type=str,
    default="~/.pi0servo_apiclient_history",
    show_default=True,
    help="History file",
)
@click_common_opts(click, __version__)
def api_cli(ctx, pins, history_file, debug):
    """API CLI"""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug("pins=%s, history_file=%s", pins, history_file)

    if not pins:
        print_pins_error(ctx)
        return

    app = None
    try:
        pi = get_pi(debug)
        app = CmdApiCli(cmd_name, pi, pins, history_file, debug=debug)
        app.main()

    except Exception as _e:
        __log.error("%s: $%s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()


@cli.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--history_file",
    type=str,
    default="~/.pi0servo_strclient_history",
    show_default=True,
    help="History file",
)
@click.option(
    "--angle_factor",
    "-a",
    type=str,
    default="1,1,1,1",
    show_default=True,
    help="Angle Factor",
)
@click_common_opts(click, __version__)
def str_cli(ctx, pins, history_file, angle_factor, debug):
    """String command CLI"""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug(
        "pins=%s, history_file=%s, angle_factor=%s",
        pins,
        history_file,
        angle_factor,
    )

    if not pins:
        print_pins_error(ctx)
        return

    af_list = [int(i) for i in angle_factor.split(",")]
    __log.debug("af_list=%s", af_list)

    app = None
    try:
        pi = get_pi(debug)
        app = CmdStrCli(
            cmd_name, pi, pins, history_file, af_list, debug=debug
        )
        app.main()

    except Exception as _e:
        __log.error("%s: $%s", type(_e).__name__, _e)

    finally:
        if app:
            app.end()


@cli.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--server_host",
    "-s",
    type=str,
    default="0.0.0.0",
    show_default=True,
    help="server hostname or IP address",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    show_default=True,
    help="port number",
)
@click_common_opts(click, __version__)
def api_server(ctx, pins, server_host, port, debug):
    """API (JSON) Server ."""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug("pins=%s", pins)
    __log.debug("server_host=%s, port=%s", server_host, port)

    if not pins:
        print_pins_error(ctx)
        return

    app = None
    try:
        app = CmdApiServer(pins, server_host, port, debug=debug)
        app.main()

    finally:
        if app:
            app.end()


@cli.command()
@click.argument("cmdline", type=str, nargs=-1)
@click.option(
    "--url",
    "-u",
    type=str,
    default="http://localhost:8000/cmd",
    show_default=True,
    help="API URL",
)
@click.option(
    "--history_file",
    type=str,
    default="~/.pi0servo_apiclient_history",
    show_default=True,
    help="History file",
)
@click_common_opts(click, __version__)
def api_client(ctx, cmdline, url, history_file, debug):
    """String API Client."""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug(
        "cmd_name=%s, url=%s, history_file=%s", cmd_name, url, history_file
    )

    __log.debug("cmdline=%a", cmdline)

    app = None
    try:
        app = CmdApiClient(cmd_name, url, cmdline, history_file, debug)
        app.main()

    except (KeyboardInterrupt, EOFError):
        pass

    finally:
        if app:
            app.end()


@cli.command()
@click.argument("cmdline", type=str, nargs=-1)
@click.option(
    "--url",
    "-u",
    type=str,
    default="http://localhost:8000/cmd",
    show_default=True,
    help="API URL",
)
@click.option(
    "--history_file",
    type=str,
    default="~/.pi0servo_strclient_history",
    show_default=True,
    help="History file",
)
@click.option(
    "--angle_factor",
    "-a",
    type=str,
    default="1,1,1,1",
    show_default=True,
    help="Angle Factor",
)
@click_common_opts(click, __version__)
def str_client(ctx, cmdline, url, history_file, angle_factor, debug):
    """String Command API Client."""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug(
        "cmd_name=%s, url=%s, history_file=%s, angle_factor=%s",
        cmd_name,
        url,
        history_file,
        angle_factor,
    )
    __log.debug("cmdline=%s", cmdline)

    af_list = [int(i) for i in angle_factor.split(",")]
    __log.debug("af_list=%s", af_list)

    app = None
    try:
        app = CmdStrClient(
            cmd_name, url, cmdline, history_file, af_list, debug
        )
        app.main()

    except (KeyboardInterrupt, EOFError):
        pass

    finally:
        if app:
            app.end()


@cli.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--server_host",
    "-s",
    type=str,
    default="0.0.0.0",
    show_default=True,
    help="server hostname or IP address",
)
@click.option(
    "--port",
    "-p",
    type=int,
    default=8000,
    show_default=True,
    help="port number",
)
@click_common_opts(click, __version__)
def jsonrpc_server(ctx, pins, server_host, port, debug):
    """JSON-RPC Server ."""
    cmd_name = ctx.command.name
    __log = get_logger(__name__, debug)
    __log.debug("cmd_name=%s", cmd_name)
    __log.debug("pins=%s", pins)
    __log.debug("server_host=%s, port=%s", server_host, port)

    if not pins:
        print_pins_error(ctx)
        return

    os.environ["PI0SERVO_DEBUG"] = "1" if debug else "0"

    click.echo("** WIP **")

    # uvicorn.run(
    #     "pi0servo.web.jsonrpc_api:app",
    #     host=server_host, port=port, reload=True
    # )

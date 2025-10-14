import json

import blessed
import click
import pigpio

from pi0servo import (
    OneKeyCli,
    StrCmdToJson,
    ThreadWorker,
    click_common_opts,
    errmsg,
    get_logger,
)

VERSION_STR = "0.0.1"


class OneKeyCmdCli(OneKeyCli):
    """One key CLI sample."""

    CMD_QUIT = "QUIT"

    KEY_BIND = {
        "d": "ms:2 mr:10,0",
        "f": "ms:2 mr:-10,0",
        "k": "ms:2 mr:0,10",
        "j": "ms:2 mr:0,-10",
        "h": "ms:2 mv:0,0",
        "q": CMD_QUIT,
        "Q": CMD_QUIT,
        "KEY_ESCAPE": CMD_QUIT,
        "\x04": CMD_QUIT,
    }

    def __init__(
        self, pi, pins, anglefactor_str: str, prompt_str, debug=False
    ):
        """Constractor."""
        super().__init__(prompt_str, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "pi=%s, pins=%s, anglefactor_str=%a", pi, pins, anglefactor_str
        )

        self.pi = pi
        self.pins = pins
        self.prompt_str = prompt_str

        self.angle_factor = self.str_to_anglefactor(anglefactor_str)
        self.__log.debug("angle_factor=%s", self.angle_factor)

        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)
        self.thr_worker = ThreadWorker(self.pi, self.pins, debug=self.__debug)
        self.term = blessed.Terminal()

    def str_to_anglefactor(self, af_str: str) -> list[int]:
        """String to angle factor."""
        self.__log.debug("af-str=%a", af_str)

        if not af_str:
            return [1] * len(self.pins)

        af = []
        try:
            af = [int(a) for a in af_str.split(",")]
        except Exception as _e:
            self.__log.error(errmsg(_e))
            raise _e

        if len(af) != len(self.pins):
            raise ValueError(f"invalid angle_factor: {af_str!r}")

        return af

    def start(self) -> bool:
        """Start."""
        if not super().start():
            return False
        self.__log.debug("")
        self.thr_worker.start()
        return True

    def end(self):
        """End."""
        self.__log.debug("")
        self.thr_worker.send({"method": "cancel"})
        self.thr_worker.send({"method": "wait"})
        self.thr_worker.end()
        super().end()

    def parse_instr(self, instr: str) -> dict:
        """Parse"""
        strcmd = self.KEY_BIND.get(instr)
        self.__log.debug("strcmd=%a", strcmd)

        if not strcmd:
            parsed_data = {
                "data": "",
                "status": self.RESULT_STATUS["OK"],
            }
            return parsed_data

        if strcmd == self.CMD_QUIT:
            parsed_data = {
                "data": self.CMD_QUIT,
                "status": self.RESULT_STATUS["EOF"],
            }
            return parsed_data

        jsoncmdliststr = self.parser.cmdstr_to_jsonliststr(strcmd)
        self.__log.debug("=%a", jsoncmdliststr)
        parsed_data = {
            "data": jsoncmdliststr,
            "status": self.RESULT_STATUS["OK"],
        }
        return parsed_data

    def handle(self, parsed_data) -> dict:
        """Handle parsed data."""
        self.__log.debug("parsed_data=%s", parsed_data)
        if parsed_data.get("data") == self.CMD_QUIT:
            raise EOFError(self.CMD_QUIT)

        result_list = []
        for jsoncmd in json.loads(parsed_data["data"]):
            result_list.append(self.thr_worker.send(jsoncmd))

        self.__log.debug("result_list=%s", result_list)
        result = {
            "data": result_list,
            "status": self.RESULT_STATUS["OK"],
        }
        return result


@click.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--anglefactor",
    "-a",
    type=str,
    default="",
    help="angle factor: e.g.'-1,1'",
)
@click_common_opts(VERSION_STR)
def main(ctx, pins, anglefactor, debug):
    """Main."""
    command_name = ctx.command.name
    __log = get_logger(command_name, debug)
    __log.debug("command_name=%s", command_name)
    __log.debug("pins=%s, anglefactor=%a", pins, anglefactor)

    if not pins:
        print(ctx.get_help())
        return

    pi = None
    app = None
    try:
        pi = pigpio.pi()
        app = OneKeyCmdCli(pi, pins, anglefactor, "> ", debug=debug)
        app.main()
    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


if __name__ == "__main__":
    main()

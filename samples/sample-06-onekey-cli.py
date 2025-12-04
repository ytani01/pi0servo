import json

import blessed
import click
import pigpio

from pi0servo import (
    CommonLib,
    OneKeyCli,
    StrCmdToJson,
    ThreadWorker,
    click_common_opts,
    get_logger,
)

VERSION_STR = "0.0.1"


class OneKeyCmdCli(OneKeyCli):
    """One key CLI sample."""

    CMD_QUIT = "QUIT"

    KEY_BIND = {
        "d": "ms:1 mr:10,0",
        "f": "ms:1 mr:-10,0",
        "k": "ms:1 mr:0,10",
        "j": "ms:1 mr:0,-10",
        "h": "ms:1 mv:0,0",
        "q": CMD_QUIT,
        "Q": CMD_QUIT,
        "KEY_ESCAPE": CMD_QUIT,
        "\x04": CMD_QUIT,
    }

    def __init__(self, pi, pins, prompt_str, debug=False):
        """Constractor."""
        super().__init__(prompt_str, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("pi=%s, pins=%s", pi, pins)

        self.pi = pi
        self.pins = pins
        self.prompt_str = prompt_str

        self.parser = StrCmdToJson(debug=self.__debug)
        self.thr_worker = ThreadWorker(self.pi, self.pins, debug=self.__debug)
        self.term = blessed.Terminal()

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
                "status": self.RESULT_STATUS["END"],
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
@click.argument("pins_str", type=str, nargs=1)
@click_common_opts(VERSION_STR)
def main(ctx, pins_str, debug):
    """Main."""
    command_name = ctx.command.name
    __log = get_logger(command_name, debug)
    __log.debug("command_name=%s", command_name)
    __log.debug("pins_str=%s", pins_str)

    clib = CommonLib(debug=debug)
    pins = clib.pins_str2list(pins_str)
    if not pins:
        print(ctx.get_help())
        return

    pi = None
    app = None
    try:
        pi = pigpio.pi()
        app = OneKeyCmdCli(pi, pins, "> ", debug=debug)
        app.main()
    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


if __name__ == "__main__":
    main()

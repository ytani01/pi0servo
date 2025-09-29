#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apicli.py"""
import json
import os
import readline  # input()でヒストリー機能が使える

from pi0servo import MultiServo, get_logger
from pi0servo.helper.thread_worker import ThreadWorker
from pi0servo.utils.clibase import CliBase


class CmdAppCliBase(CliBase):
    """CLI base"""
    def __init__(self, prefix, hist, thworker, debug=False):
        """constractor"""
        super().__init__(prefix, hist, debug=debug)
        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)

        self.thworker = thworker
        
    def parse_line(self, line: str) -> str:
        """parse command line string to json"""

        # {"method": "move", ..} を {'method': 'move', ..}
        # のように誤入力した場合の対応
        parsed_line = line.replace("'", "\"")
        self.__log.debug("parsed_line=%a", parsed_line)
        return parsed_line

    def send(self, line):
        """Send"""
        self.__log.debug("line=%a", line)

        line_json = json.loads(line)
        try:
            for _j in line_json:
                print(f"> {_j}")
                _res = self.thworker.send(_j)
                print(f"* {_res}")

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)


class CmdApiCli:
    """CmdApiCli."""

    PROMPT_STR = "> "

    def __init__(
            self, cmd_name, pi, pins, history_file, debug=False
    ) -> None:
        """constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, pins=%s, history_file=%s",
            cmd_name, pins, history_file
        )

        self.pi = pi
        self.cmd_name = cmd_name
        self.pins = pins
        self.history_file = history_file

        try:
            self.mservo = MultiServo(self.pi, self.pins, debug=False)
            self.tworker = ThreadWorker(self.mservo, debug=self.__debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

        self.cli = CmdAppCliBase(
            self.cmd_name, self.history_file, self.tworker, debug=self.__debug
        )

    def print_response(self, _res):
        """print response in json format"""
        self.__log.debug("_res='%s': %s", _res, type(_res))
        try:
            print(f"* > {_res.json()}")
        except Exception:
            print(f"* {_res}")

    def parse_cmdline(self, cmdline: str) -> str:
        """parse command line string to json

        *** To Be Override ***

        """
        # {"method": "move", ..} を {'method': 'move', ..}
        # のように誤入力した場合の対応
        cmdline = cmdline.replace("'", "\"")
        return cmdline

    def main(self):
        """main loop"""
        self.tworker.start()
        self.cli.loop()

    def end(self):
        """end"""
        if self.tworker:
            self.tworker.end()
        print("\n* Bye\n")

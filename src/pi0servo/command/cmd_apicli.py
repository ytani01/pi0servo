
#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apicli.py"""
import json
import os
import readline  # input()でヒストリー機能が使える

from pi0servo import MultiServo, get_logger
from pi0servo.helper.thread_worker import ThreadWorker


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
        self.history_file = os.path.expanduser(history_file)

        try:
            self.mservo = MultiServo(self.pi, self.pins, debug=False)
            self.tworker = ThreadWorker(self.mservo, debug=self.__debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

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
        #
        # interactive mode
        #
        self.tworker.start()

        try:
            # read history file
            try:
                readline.read_history_file(self.history_file)
            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)

            print(f"* history file: {self.history_file}")
            self.__log.debug(
                "history_length=%s",
                readline.get_current_history_length()
            )

        except FileNotFoundError:
            self.__log.debug("no history file: %s", self.history_file)

        # start interactive mode
        print("* Ctrl-C (Interrput) or Ctrl-D (EOF) for quit")

        try:
            while True:
                try:
                    _line = input(self.cmd_name + self.PROMPT_STR)
                    _line = _line.strip()
                    self.__log.debug("_line=%a", _line)
                    readline.write_history_file(self.history_file)

                except (KeyboardInterrupt, EOFError):
                    break

                if not _line:
                    self.__log.debug("%a: ignored", _line)
                    continue

                if _line.startswith("#"):
                    self.__log.debug("%a: ignored", _line)
                    continue

                _parsed_json = json.loads(self.parse_cmdline(_line))
                self.__log.debug("parsed_json=%s", _parsed_json)
                try:
                    for _j in _parsed_json:
                        _res = self.tworker.send(_j)
                        self.print_response(_res)
                except Exception as _e:
                    self.__log.error("%s: %s", type(_e).__name__, _e)

        finally:
            self.__log.debug("save history: %s", self.history_file)
            readline.write_history_file(self.history_file)

    def end(self):
        """end"""
        if self.tworker:
            self.tworker.end()
        print("\n* Bye\n")

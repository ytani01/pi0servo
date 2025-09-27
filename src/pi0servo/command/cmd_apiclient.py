
#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiclient.py"""
import json
import os
import readline  # input()でヒストリー機能が使える

from pi0servo import ApiClient, get_logger


class CmdApiClient:
    """CmdApiClient."""

    PROMPT_STR = "> "

    def __init__(
            self, cmd_name, url, cmdline: tuple, history_file, debug=False
    ) -> None:
        """constractor."""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("cmd_name=%s, url=%s", cmd_name, url)
        self.__log.debug("cmdline=%a", cmdline)

        self.cmd_name = cmd_name
        self.url = url
        self.cmdline = cmdline
        self.history_file = os.path.expanduser(history_file)
        self.__log.debug("cmd_name=%s, url=%s", self.cmd_name, self.url)
        self.__log.debug("cmdline=%s", self.cmdline)
        self.__log.debug("history_file=%s", self.history_file)

        try:
            self.api_client = ApiClient(self.url, self._debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def print_response(self, _res):
        """print response in json format"""
        self.__log.debug("_res='%s': %s", _res, type(_res))
        try:
            print(f"* {self.url}> {_res.json()}")
        except Exception:
            print(f"* {_res}")

    def parse_cmdline(self, cmdline: str) -> str:
        """parse command line string to json

        *** To Be Override ***

        """
        # {"cmd": "move"} を {'cmd': 'move'} のように誤入力した場合の対応
        return cmdline.replace("'", "\"")

    def main(self):
        """main loop"""

        if self.cmdline:
            #
            # command arguments mode
            #
            for _l in self.cmdline:
                self.__log.debug("_l=%s", _l)

                _parsed_line = self.parse_cmdline(_l)
                try:
                    _res = self.api_client.post(_parsed_line)
                    self.print_response(_res)
                except Exception as _e:
                    self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        #
        # interactive mode
        #
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

                _parsed_line = self.parse_cmdline(_line)
                try:
                    _res = self.api_client.post(_parsed_line)
                except Exception as _e:
                    self.__log.error("%s: %s", type(_e).__name__, _e)
                    _res = type(_e).__name__
                self.print_response(_res)

        finally:
            self.__log.debug("save history: %s", self.history_file)
            readline.write_history_file(self.history_file)

    def end(self):
        """end"""
        print("\n* Bye\n")

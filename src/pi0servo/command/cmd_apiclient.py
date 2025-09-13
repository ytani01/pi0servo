
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

        self.api_client = ApiClient(self.url, self._debug)

    def print_response(self, _res):
        """print response in json format"""
        print(f"* {self.url}> {json.dumps(_res.json())}")

    def parse_cmdline(self, cmdline):
        """parse command line string to json

        *** To Be Override ***

        """
        return cmdline

    def main(self):
        """main loop"""

        if self.cmdline:
            #
            # command arguments mode
            #
            for _l in self.cmdline:
                self.__log.debug("_l=%s", _l)

                _parsed_line = self.parse_cmdline(_l)
                _res = self.api_client.post(_parsed_line)
                self.print_response(_res)
            return

        #
        # interactive mode
        #
        try:
            # read history file
            readline.read_history_file(self.history_file)
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
                _res = self.api_client.post(_parsed_line)
                self.print_response(_res)

        finally:
            self.__log.debug("save history: %s", self.history_file)
            readline.write_history_file(self.history_file)

    def end(self):
        """end"""
        print("\n* Bye\n")


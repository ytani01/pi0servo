#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiclient.py"""
import json

from pi0servo import ApiClient, get_logger

from ..utils.clibase import CliBase


class CmdApiClientInteractive(CliBase):
    """CmdApiClient Ineractive base."""

    def __init__(self, prefix, hist, cmdline, url, debug=False):
        """Constractor."""

        super().__init__(prefix, hist, debug=debug)

        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)
        self.__log.debug("cmdline=%s", cmdline)
        self.__log.debug("url=%s", url)

        self.url = url
        self.cmdline = cmdline
        try:
            self.api_client = ApiClient(self.url, debug=self.__debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def parse_line(self, line: str) -> str:
        """parse command line string to json

        *** To Be Override ***

        Return:
            リスト形式のコマンド列を文字列に変換
        """
        self.__log.debug("line=%a", line)

        # {"method": "move"} を {'cmd': 'move'} のように誤入力した場合の対応
        parsed_line = line.replace("'", "\"")

        try:
            # JSON形式の確認のため、デコードしてみる
            _ = json.loads(parsed_line)

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return ""

        self.__log.debug("parsed_line=%a", parsed_line)
        return parsed_line

    def send(self, line: str):
        """Send line."""
        self.__log.debug("line=%a", line)

        try:
            line_json = json.loads(line)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        if not isinstance(line_json, list):
            line_json = [line_json]

        for _j in line_json:
            try:
                print(f">>> {json.dumps(_j)}", flush=True)

                res = self.api_client.post(_j)

                print(f" <<< {self.url}: {res}")
            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)


class CmdApiClient:
    """CmdApiClient."""

    def __init__(
            self, cmd_name, url, cmdline: tuple, history_file, debug=False
    ) -> None:
        """constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("cmd_name=%s, url=%s", cmd_name, url)
        self.__log.debug("cmdline=%a", cmdline)
        self.__log.debug("history_file=%a", history_file)

        self.cmd_name = cmd_name
        self.url = url
        self.cmdline = cmdline
        self.history_file = history_file

        self.cli = CmdApiClientInteractive(
            self.cmd_name, self.history_file, self.cmdline, self.url,
            debug=self.__debug
        )

    def main(self):
        """main loop"""
        self.cli.loop()

    def end(self):
        """end"""
        print("\n* Bye\n")

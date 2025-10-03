#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiclient.py"""

import json

from pyclibase import CliBase
from pyclickutils import get_logger

from pi0servo import ApiClient


class CmdApiClient(CliBase):
    """CmdApiClient."""

    def __init__(
        self, cmd_name, url, history_file, script_file, debug=False
    ) -> None:
        """Constractor."""
        super().__init__(cmd_name, history_file, script_file, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("cmd_name=%s, url=%s", cmd_name, url)

        self.url = url

        try:
            self.api_client = ApiClient(self.url, debug=self.__debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def end(self):
        """end"""
        self.__log.debug("")
        super().end()
        print("\n* Bye\n")

    def parse_line(self, line: str) -> str:
        """parse command line string to json

        Return:
            リスト形式のコマンド列を文字列に変換
        """
        self.__log.debug("line=%a", line)

        # {"method": "move"} を {'cmd': 'move'} のように誤入力した場合の対応
        parsed_line = line.replace("'", '"')

        try:
            parsed_line_json = json.loads(parsed_line)
        except json.JSONDecodeError as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            parsed_line_json = {"error": "INVALID_JSON", "data": line}
            return ""

        if not isinstance(parsed_line_json, list):
            parsed_line = json.dumps([parsed_line_json])

        self.__log.debug("parsed_line=%a", parsed_line)
        return parsed_line

    def exec(self, line: str) -> str:
        """Send line."""
        self.__log.debug("line=%a", line)

        try:
            line_json = json.loads(line)
        except Exception as _e:
            msg = f"{type(_e).__name__}: {_e}"
            self.__log.error(msg)
            return msg

        if not isinstance(line_json, list):
            line_json = [line_json]
        self.__log.debug("line_json=%s", line_json)

        result_json = []
        for _j in line_json:
            try:
                print(f">>> {json.dumps(_j)}", flush=True)
                res = self.api_client.post(_j)
                print(f" <<< {self.url}: {res}")
                result_json.append(res)
            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)
                return ""
        return json.dumps(result_json)

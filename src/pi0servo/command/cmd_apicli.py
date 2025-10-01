#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apicli.py"""

import json

from pyclibase import CliBase

from pi0servo import MultiServo, get_logger
from pi0servo.helper.thread_worker import ThreadWorker


class CmdAppCliBase(CliBase):
    """CLI base"""

    def __init__(self, prefix, hist, thworker, debug=False):
        """constractor"""

        super().__init__(prefix, hist, debug=debug)

        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)

        self.thworker = thworker

    def parse_line(self, line: str) -> str:
        """parse command line string to json string"""

        # {"method": "move", ..} を {'method': 'move', ..}
        # のように誤入力した場合の対応
        parsed_line = line.replace("'", '"')

        try:
            parsed_line_json = json.loads(parsed_line)
        except json.JSONDecodeError as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            parsed_line_json = {"error": "INVALID_JSON", "data": line}

        if not isinstance(parsed_line_json, list):
            parsed_line = json.dumps([parsed_line_json])

        self.__log.debug("parsed_line=%a", parsed_line)
        return parsed_line

    def exec(self, line: str) -> str:
        """Execute line."""
        self.__log.debug("line=%a", line)

        line_json = json.loads(line)
        if not isinstance(line_json, list):
            line_json = [line_json]
        self.__log.debug("line_json=%s", line_json)

        result_json = []
        try:
            for _j in line_json:
                print(f">>> {_j}", flush=True)
                _res = self.thworker.send(_j)
                print(f" <<< {_res}", flush=True)
                result_json.append(_res)

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return ""

        return json.dumps(result_json)


class CmdApiCli:
    """CmdApiCli."""

    def __init__(self, cmd_name, pi, pins, history_file, debug=False) -> None:
        """constractor."""

        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, pins=%s, history_file=%s",
            cmd_name,
            pins,
            history_file,
        )

        self.pi = pi
        self.cmd_name = cmd_name
        self.pins = pins
        self.history_file = history_file

        try:
            self.mservo = MultiServo(self.pi, self.pins, debug=False)
            self.thworker = ThreadWorker(self.mservo, debug=self.__debug)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

        self.cli = CmdAppCliBase(
            self.cmd_name,
            self.history_file,
            self.thworker,
            debug=self.__debug,
        )

    def main(self):
        """main loop"""
        self.thworker.start()
        self.cli.loop()

    def end(self):
        """end"""
        self.__log.debug("")

        if self.thworker:
            self.thworker.end()
        print("\n* Bye\n")

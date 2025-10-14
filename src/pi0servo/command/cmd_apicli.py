#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apicli.py"""

import json

from pi0servo import (
    CliBase,
    CliWithHistory,
    ScriptRunner,
    ThreadWorker,
    errmsg,
    get_logger,
)


class CmdApiCommon:
    """CmdApiCommon"""

    def __init__(self, pi, pins, debug=False):
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, debug=self.__debug)
        self.__log.debug("pins=%s", pins)

        self.pi = pi
        self.pins = pins

        try:
            self.thr_worker = ThreadWorker(self.pi, self.pins, debug=False)
        except Exception as _e:
            msg = errmsg(_e)
            self.__log.error(msg)
            raise Exception(msg)

    def start(self):
        """Start."""
        self.thr_worker.start()

    def end(self):
        """End."""
        if self.thr_worker:
            self.thr_worker.end()

    def parse_instr(self, instr: str) -> dict:
        """parse command string to json string"""

        # {"method": "move"} を {'cmd': 'move'} のように誤入力した場合の対応
        parsed_instr = instr.replace("'", '"')

        try:
            parsed_json = json.loads(parsed_instr)
        except json.JSONDecodeError as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            parsed_data = {
                "data": {"error": "INVALID_JSON", "data": instr},
                "status": CliBase.RESULT_STATUS["ERR"],
            }
            self.__log.debug("parsed_data=%s", parsed_data)
            return parsed_data

        if not isinstance(parsed_json, list):
            parsed_json = [parsed_json]

        parsed_data = {
            "data": parsed_json,
            "status": CliBase.RESULT_STATUS["OK"],
        }
        self.__log.debug("parsed_data=%s", parsed_data)
        return parsed_data

    def handle(self, parsed_data: dict) -> dict:
        """Execute line."""
        self.__log.debug("parsed_data=%s", parsed_data)

        try:
            cmd_json = parsed_data["data"]
        except Exception as _e:
            msg = f"{type(_e).__name__}: {_e}"
            self.__log.error(msg)
            result_data = {
                "data": msg,
                "status": CliBase.RESULT_STATUS["ERR"],
            }
            return result_data

        if not isinstance(cmd_json, list):
            cmd_json = [cmd_json]
        self.__log.debug("cmd_json=%s", cmd_json)

        result_json = []
        try:
            for _j in cmd_json:
                print(f">>> {_j}", flush=True)
                _res = self.thr_worker.send(_j)

                print(f" <<< {_res}", flush=True)
                result_json.append(_res)
        except Exception as _e:
            msg = errmsg(_e)
            self.__log.error(msg)
            result_data = {
                "data": msg,
                "status": CliBase.RESULT_STATUS["ERR"],
            }
            return result_data

        result_data = {
            "data": result_json,
            "status": CliBase.RESULT_STATUS["OK"],
        }
        return result_data


class CmdApiCli(CliWithHistory):
    """CmdApiCli."""

    def __init__(
        self, prompt_str, pi, pins, history_file, debug=False
    ) -> None:
        """Constractor."""
        super().__init__(prompt_str, history_file, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("pins=%s", pins)

        self.common = CmdApiCommon(pi, pins, debug=self.__debug)

    def start(self) -> bool:
        self.__log.debug("")
        if super().start():
            self.common.start()
            return True
        return False

    def end(self):
        """end"""
        self.__log.debug("end_flag=%s", self.end_flag)
        if self.end_flag:
            return
        self.common.end()
        print("\n* Bye!\n")
        super().end()

    def parse_instr(self, instr: str) -> dict:
        """parse command string to json string"""
        self.__log.debug("instr=%a", instr)
        return self.common.parse_instr(instr)

    def handle(self, parsed_data: dict) -> dict:
        """Execute line."""
        self.__log.debug("parsed_data=%s", parsed_data)
        return self.common.handle(parsed_data)


class CmdApiScriptRunner(ScriptRunner):
    """CmdApiScriptRunner"""

    def __init__(self, pi, pins, script_file, debug=False):
        """Constractor."""
        super().__init__(script_file, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, debug=self.__debug)
        self.__log.debug("pins=%s", pins)

        self.common = CmdApiCommon(pi, pins, debug=self.__debug)

    def start(self) -> bool:
        self.__log.debug("")
        if super().start():
            self.common.start()
            return True
        return False

    def end(self):
        """end"""
        self.__log.debug("end_flag=%s", self.end_flag)
        return self.common.end()

    def parse_instr(self, instr: str) -> dict:
        """parse command string to json string"""
        self.__log.debug("instr=%a", instr)
        return self.common.parse_instr(instr)

    def handle(self, parsed_data: dict) -> dict:
        """Execute line."""
        self.__log.debug("parsed_data=%s", parsed_data)
        return self.common.handle(parsed_data)

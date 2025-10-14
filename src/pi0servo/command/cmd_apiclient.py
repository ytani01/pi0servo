#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiclient.py"""

import json

from pi0servo import ApiClient, CliWithHistory, errmsg, get_logger


class CmdApiClient(CliWithHistory):
    """CmdApiClient."""

    def __init__(
        self, cmd_name, url, history_file, script_file, debug=False
    ) -> None:
        """Constractor."""
        super().__init__(cmd_name, history_file, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("cmd_name=%s, url=%s", cmd_name, url)

        self.url = url

        try:
            self.api_client = ApiClient(self.url, debug=self.__debug)
        except Exception as _e:
            self.__log.error(errmsg(_e))

    def end(self):
        """end"""
        self.__log.debug("")
        super().end()
        print("\n* Bye\n")

    def parse_instr(self, instr: str) -> dict:
        """parse string to json"""
        self.__log.debug("instr=%a", instr)

        parsed_instr = instr.replace("'", '"')

        try:
            parsed_json = json.loads(parsed_instr)
        except json.JSONDecodeError as _e:
            self.__log.warning("%s: %s", type(_e).__name__, _e)
            parsed_json = {"error": "INVALID_JSON", "data": instr}
            parsed_data = {
                "data": parsed_json,
                "status": self.RESULT_STATUS["ERR"],
            }
            return parsed_data

        if not isinstance(parsed_json, list):
            parsed_json = json.dumps([parsed_json])

        parsed_data = {
            "data": parsed_json,
            "status": self.RESULT_STATUS["OK"],
        }
        self.__log.debug("parsed_data=%a", parsed_data)
        return parsed_data

    def handle(self, parsed_data: dict) -> dict:
        """Send parsed_data."""
        self.__log.debug("parsed_data=%a", parsed_data)

        cmd_json = parsed_data.get("data")

        if not cmd_json:
            result_data = {"data": "", "status": self.RESULT_STATUS["ERR"]}
            return result_data

        if not isinstance(cmd_json, list):
            cmd_json = [cmd_json]

        result_json = []
        for _j in cmd_json:
            try:
                print(f">>> {json.dumps(_j)}", flush=True)
                res = self.api_client.post(_j)

                print(f" <<< {self.url}: {res}")
                result_json.append(res)

            except Exception as _e:
                msg = errmsg(_e)
                self.__log.error(msg)
                return {"data": msg, "status": self.RESULT_STATUS["ERR"]}

        return {"data": result_json, "status": self.RESULT_STATUS["OK"]}

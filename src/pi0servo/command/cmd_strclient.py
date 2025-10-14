#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""

from pi0servo import StrCmdToJson, get_logger

from .cmd_apiclient import CmdApiClient


class CmdStrClient(CmdApiClient):
    """CmdStrClient."""

    def __init__(
        self,
        cmd_name,
        url,
        history_file,
        script_file,
        angle_factor,
        debug=False,
    ):
        super().__init__(
            cmd_name, url, history_file, script_file, debug=debug
        )
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("angle_factor=%s", angle_factor)

        self.angle_factor = angle_factor

        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)

    def parse_instr(self, instr: str) -> dict:
        """parse string command to json.

        **TBD**
        parse errors
        """
        self.__log.debug("instr=%s", instr)

        parsed_json = self.parser.cmdstr_to_jsonlist(instr)
        self.__log.debug("parsed_json=%s", parsed_json)

        return {"data": parsed_json, "status": self.RESULT_STATUS["OK"]}

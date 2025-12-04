#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""

from pi0servo import StrCmdToJson, get_logger

from .cmd_apicli import CmdApiCli


class CmdStrCli(CmdApiCli):
    """CmdStrCli."""

    def __init__(
        self,
        cmd_name,
        pi,
        pins,
        history_file,
        debug=False,
    ) -> None:
        """Constractor."""
        super().__init__(cmd_name, pi, pins, history_file, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("cmd_name=%s, pins=%s", cmd_name, pins)

        self.parser = StrCmdToJson(debug=self.__debug)

    def parse_instr(self, instr: str) -> dict:
        """Parse comand line to json stirng"""
        self.__log.debug("instr=%a", instr)

        parsed_json = self.parser.cmdstr_to_jsonlist(instr)
        self.__log.debug("parsed_json=%a", parsed_json)
        return {"data": parsed_json, "status": self.RESULT_STATUS["OK"]}

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

    def parse_line(self, line: str) -> str:
        """parse string command to json."""
        self.__log.debug("line=%s", line)

        parsed_line = self.parser.cmdstr_to_jsonliststr(line)
        self.__log.debug("parsed_line=%s", parsed_line)

        return parsed_line

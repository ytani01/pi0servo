#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""
from pi0servo import StrCmdToJson, get_logger

from .cmd_apicli import CmdApiCli


class CmdStrCli(CmdApiCli):
    """CmdStrClient."""

    def __init__(
        self, cmd_name, pi, pins, history_file, angle_factor, debug=False
    ) -> None:
        """constractor."""
        super().__init__(cmd_name, pi, pins, history_file, debug)

        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, pins=%s, history_file=%s, angle_factor=%s",
            cmd_name, pins, history_file, angle_factor
        )

        self._angle_factor = angle_factor

        self.parser = StrCmdToJson(self._angle_factor, debug=self.__debug)

    def parse_cmdline(self, cmdline: str) -> str:
        """parse string command to json string."""
        self.__log.debug("cmdline=%s", cmdline)

        parsed_str = self.parser.cmdstr_to_jsonliststr(cmdline)
        self.__log.debug("parsed_str=%s", parsed_str)

        return parsed_str

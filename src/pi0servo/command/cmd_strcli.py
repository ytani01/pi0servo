#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""
from pi0servo import StrCmdToJson, get_logger

from .cmd_apicli import CmdApiCli, CmdAppCliBase


class CmdStrCliBase(CmdAppCliBase):
    """CLI base"""

    def __init__(self, prefix, hist, thworker, angle_factor, debug=False):
        """constractor"""

        super().__init__(prefix, hist, thworker, debug=debug)

        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)
        self.__log.debug("angle_factor=%s", angle_factor)

        self.angle_factor = angle_factor
        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)

    def parse_line(self, line):
        """Parse comand line to json stirng"""
        self.__log.debug("line=%a", line)

        parsed_str = self.parser.cmdstr_to_jsonliststr(line)
        self.__log.debug("parsed_str=%a", parsed_str)
        return parsed_str


class CmdStrCli(CmdApiCli):
    """CmdStrClient."""

    def __init__(
        self, cmd_name, pi, pins, history_file, angle_factor, debug=False
    ) -> None:
        """constractor."""

        super().__init__(cmd_name, pi, pins, history_file, debug=debug)

        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, pins=%s, history_file=%s, angle_factor=%s",
            cmd_name, pins, history_file, angle_factor
        )

        self.angle_factor = angle_factor

        self.cli = CmdStrCliBase(
            self.cmd_name, self.history_file,
            self.thworker, self.angle_factor,
            debug=self.__debug
        )

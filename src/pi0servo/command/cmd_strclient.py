#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_strclient.py."""

from pi0servo import StrCmdToJson, get_logger

from .cmd_apiclient import CmdApiClient, CmdApiClientInteractive


class CmdStrClientInteractive(CmdApiClientInteractive):
    """CmdStrClient Interactive base."""

    def __init__(
            self, prefix, hist, cmdline, url, angle_factor, debug=False
    ):
        super().__init__(prefix, hist, cmdline, url)

        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)
        self.__log.debug("cmdline=%s", cmdline)
        self.__log.debug("angle_factor=%s", angle_factor)

        self.cmdline = cmdline
        self.angle_factor = angle_factor

        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)

    def parse_line(self, line: str) -> str:
        """parse string command to json."""
        self.__log.debug("line=%s", line)

        parsed_str = self.parser.cmdstr_to_jsonliststr(line)
        self.__log.debug("parsed_str=%s", parsed_str)

        return parsed_str


class CmdStrClient(CmdApiClient):
    """CmdStrClient."""

    def __init__(
        self, cmd_name, url, cmdline, history_file, angle_factor, debug=False
    ):
        super().__init__(cmd_name, url, cmdline, history_file, debug)

        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, angle_factor=%s", cmd_name, angle_factor
        )

        self.cmd_name = cmd_name
        self.url = url
        self.cmdline = cmdline
        self.history_file = history_file
        self.angle_factor = angle_factor

        self.cli = CmdStrClientInteractive(
            self.cmd_name, self.history_file, self.cmdline, self.url,
            self.angle_factor, debug=self.__debug
        )

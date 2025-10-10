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
        script_file,
        angle_factor,
        debug=False,
    ) -> None:
        """Constractor."""
        super().__init__(
            cmd_name, pi, pins, history_file, script_file, debug=debug
        )
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "cmd_name=%s, pins=%s, angle_factor=%s",
            cmd_name,
            pins,
            angle_factor,
        )

        self.angle_factor = angle_factor
        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)

    def parse_line(self, line):
        """Parse comand line to json stirng"""
        self.__log.debug("line=%a", line)

        parsed_str = self.parser.cmdstr_to_jsonliststr(line)
        self.__log.debug("parsed_str=%a", parsed_str)
        return parsed_str

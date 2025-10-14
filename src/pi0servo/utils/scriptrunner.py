import os

from .clibase import CliBase
from .mylogger import errmsg, get_logger


class ScriptRunner(CliBase):
    """Script Runner."""

    def __init__(self, script_file, debug=False):
        super().__init__("", debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, debug=self.__debug)
        self.__log.debug("script_file=%a", script_file)

        self.script_file = script_file
        self.script_f = None

    def start(self):
        """Start."""
        # init script_file
        self.script_file = os.path.expanduser(
            os.path.expandvars(self.script_file)
        )
        self.__log.debug("script_file=%a", self.script_file)

        try:
            self.script_f = open(self.script_file, "r", encoding="utf-8")
        except Exception as _e:
            self.script_f = None
            msg = errmsg(_e)
            self.__log.error(msg)
            return False

        return True

    def end(self):
        """End."""
        self.__log.debug("end_flag=%s", self.end_flag)
        if self.end_flag:
            return

        if self.script_f:
            self.script_f.close()

        super().end()

    def input_data(self) -> str:
        """Read line."""
        if self.script_f:
            instr = self.script_f.readline()
            self.__log.debug("instr=%a(%s)", instr, type(instr).__name__)
            if instr:
                return instr
        raise EOFError

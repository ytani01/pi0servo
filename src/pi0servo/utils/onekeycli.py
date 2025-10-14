import blessed

from .clibase import CliBase
from .mylogger import get_logger


class OneKeyCli(CliBase):
    """One key CLI"""

    KEY_EOF = "\x04"
    CMD_EXIT = [
        KEY_EOF,
        "Q",
        "q",
    ]

    def __init__(self, prompt_str="> ", debug=False):
        super().__init__(prompt_str, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, debug=self.__debug)
        self.__log.debug("")

        self.term = blessed.Terminal()

    def input_data(self) -> str:
        """Read line."""
        instr = ""
        with self.term.cbreak():
            if self.prompt_str:
                print(self.prompt_str, end="", flush=True)
            instr = self.term.inkey()

            if instr.is_sequence:
                instr = instr.name
            else:
                instr = str(instr)
            self.__log.debug("instr=%a(%s)", instr, type(instr).__name__)
            print(f"{instr!r}")

            if instr in self.CMD_EXIT:
                raise EOFError

        if instr is None:
            instr = ""
        return instr

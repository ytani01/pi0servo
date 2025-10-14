#
# (c) 2025 Yoichi Tanibayashi
#
"""CLI with hisotry"""

import os
import readline

from .clibase import CliBase
from .mylogger import errmsg, get_logger


class CliWithHistory(CliBase):
    """CLI with history"""

    HIST_LEN = 500

    def __init__(
        self,
        prompt_str: str = CliBase.PROMPT_STR,
        history_file: str = "",
        debug=False,
    ):
        """Contractor."""
        super().__init__(prompt_str, debug=debug)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("history_file=%a", history_file)

        self.history_file = history_file

    def start(self) -> bool:
        """Start.
        **TO BE OVERRIDE**

        Returns:
            ret (bool)
        """
        # init history
        if self.history_file:
            self.history_file = os.path.expanduser(
                os.path.expandvars(self.history_file)
            )
            self.__log.debug("history_file=%a", self.history_file)

            try:
                readline.read_history_file(self.history_file)
                readline.set_history_length(self.HIST_LEN)
                self.__log.debug("hist_len=%s", readline.get_history_length())
                self.__log.debug(
                    "cur_hist_len=%s", readline.get_current_history_length()
                )
            except FileNotFoundError:
                self.__log.debug("no history file: %s", self.history_file)
            except OSError:
                self.__log.warning(
                    "invalid history file .. remove: %s", self.history_file
                )
                # ヒストリーファイルが壊れていると思われるので削除する。
                os.remove(self.history_file)
            except Exception as _e:
                self.__log.error(errmsg(_e))

        return True

    def end(self):
        """End.
        **TO BE OVERRIDE**
        """
        self.__log.debug("end_flag=%s", self.end_flag)
        if self.end_flag:
            return

        if self.history_file:
            self.__log.debug("save history: %s", self.history_file)
            try:
                readline.write_history_file(self.history_file)
            except Exception as _e:
                self.__log.error(f"{self.history_file!r}: {errmsg(_e)}")

        super().end()

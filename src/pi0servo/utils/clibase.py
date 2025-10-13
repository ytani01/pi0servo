#
# (c) 2025 Yoichi Tanibayashi
#
"""CLI base"""

import os
import readline

from .mylogger import errmsg, get_logger


class CliBase:
    """CLI base class"""

    PROMPT_STR = "> "
    COMMENT_STR = "#"

    HIST_LEN = 500

    RESULT_STATUS = {
        "OK": 0,
        "END": -1,
        "ERR": 1,
    }

    def __init__(
        self,
        prompt_str: str = PROMPT_STR,
        history_file: str = "",
        debug=False,
    ):
        """Contractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "prompt_str=%a, history_file=%a", prompt_str, history_file
        )

        self.prompt_str = prompt_str
        self.history_file = history_file

        self.end_flag = False  # end()が一度でも呼ばれると True

    def main(self):
        """Main."""
        self.__log.debug("")
        try:
            if self.start():
                self.loop()
        finally:
            self.end()

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
                self.__log.error("%s: %s", type(_e).__name__, _e)

        return True

    def end(self):
        """End.
        **TO BE OVERRIDE**
        """
        self.__log.debug("end_flag=%s", self.end_flag)

        if self.end_flag:
            return

        self.__log.debug("history_file=%a", self.history_file)
        if self.history_file:
            self.__log.debug("save history: %s", self.history_file)
            try:
                readline.write_history_file(self.history_file)
            except Exception as _e:
                self.__log.error(f"{self.history_file!r}: {errmsg(_e)}")

        self.end_flag = True
        self.__log.debug("done")

    def input_data(self) -> str:
        """Key input."""
        return input(self.prompt_str)

    def parse_instr(self, instr: str) -> dict:
        """Parse input string.
        **TO BE OVERRIDE**

        Args:
            instr (str): 入力された文字列

        Returns:
            parsed_data (dict):
                {
                    "data": (Any)
                    "status": 0  # OK
                }
        """
        self.__log.debug("instr=%a", instr)

        instr = instr.strip()

        parsed_data = {
            "data": instr,
            "status": 0
        }
        return parsed_data

    def handle(self, parsed_data: dict) -> dict:
        """handle parsed data.
        **TO BE OVERRIDE**

        Args:
            parsed_data (dict):

        Returns:
            result (dict):
                {"data": (Any), "status": self.RESULT_STATUS[?]}
        """
        self.__log.debug("parsed_data=%s", parsed_data)
        if parsed_data.get("status") != 0:
            self.__log.warning("Invalid parsed_data: %s", parsed_dta)
            result = {
                "data": f"Invalid parsed_data: {parsed_data}",
                "status": self.RESULT_STATUS['ERR']
            }
            return result

        result_data = parsed_data.get("data")

        result = {
            "data": result_data,
            "status": self.RESULT_STATUS["OK"]
        }
        return result

    def process_instr(self, instr: str) -> dict:
        """Process input data.

        Args:
            instr (str):

        Returns:
            result (dict):
                {
                    "data": (Any),
                    "status": self.RESULT_STATUS[?]
                }
        """
        self.__log.debug("instr=%a", instr)

        parsed_data = self.parse_instr(instr)
        self.__log.debug("parsed_data=%s", parsed_data)
        if parsed_data.get("status") != self.RESULT_STATUS['OK']:
            self.__log.warning(f"parse error: {parsed_data.get('status')}")
            return parsed_data

        result = {
            "data": None,
            "status": self.RESULT_STATUS["OK"]
        }
        try:
            result = self.handle(parsed_data)
            self.__log.debug("result=%s", result)
            if result.get('status') == self.RESULT_STATUS["OK"]:
                print(f"result.data> {result.get('data')}")
            else:
                print(f"ERROR:{result.get('status')}> {result.get('data')}")
        except Exception as _e:
            msg = errmsg(_e)
            self.__log.warning(msg)
            result = {
                "data": msg,
                "status": self.RESULT_STATUS["ERR"]
            }
        return result

    def loop(self):
        """loop"""
        try:
            while True:
                try:
                    instr = self.input_data()
                    self.__log.debug("instr=%a", instr)
                except EOFError as _e:
                    print("[EOF]")
                    self.__log.debug(errmsg(_e))
                    break

                result = self.process_instr(instr)
                if result.get("status") == self.RESULT_STATUS["END"]:
                    break

        except KeyboardInterrupt as _e:
            print("^C [Interrupt]")
            self.__log.debug(errmsg(_e))

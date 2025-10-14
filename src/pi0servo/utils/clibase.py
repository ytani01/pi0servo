#
# (c) 2025 Yoichi Tanibayashi
#
"""CLI base"""

from .mylogger import errmsg, get_logger


class CliBase:
    """CLI base class"""

    PROMPT_STR = "> "

    RESULT_STATUS = {
        "OK": 0,
        "END": -1,
        "ERR": 1,
    }

    def __init__(self, prompt_str: str = PROMPT_STR, debug=False):
        """Contractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("prompt_str=%a", prompt_str)

        self.prompt_str = prompt_str

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
        return True

    def end(self):
        """End.
        **TO BE OVERRIDE**
        """
        self.__log.debug("end_flag=%s", self.end_flag)
        if self.end_flag:
            return

        self.end_flag = True
        self.__log.debug("done")

    def input_data(self) -> str:
        """Key input.
        **TO BE OVERRIDE**
        """
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

        parsed_data = {"data": instr, "status": self.RESULT_STATUS["OK"]}
        return parsed_data

    def handle(self, parsed_data: dict) -> dict:
        """handle parsed data.
        **TO BE OVERRIDE**

        Args:
            parsed_data (dict):

        Returns:
            result (dict):
                {"data": "", "status": self.RESULT_STATUS[?]}
        """
        self.__log.debug("parsed_data=%s", parsed_data)
        if parsed_data.get("status") != self.RESULT_STATUS["OK"]:
            self.__log.warning("Invalid parsed_data: %s", parsed_data)
            result_data = {
                "data": f"Invalid parsed_data: {parsed_data}",
                "status": self.RESULT_STATUS["ERR"],
            }
            return result_data

        data = parsed_data.get("data")
        result = data  # result = something(data)

        result_data = {"data": result, "status": self.RESULT_STATUS["OK"]}
        self.__log.debug("result_data=%s", result_data)
        return result_data

    def output_result(self, result_data: dict):
        """Output result."""
        data = result_data.get("data")
        status = result_data.get("status")

        if status == self.RESULT_STATUS["OK"]:
            print(f"result.data> {data}")
        else:
            print(f"ERROR:{status}> {data}")

    def loop(self):
        """loop"""
        self.__log.debug("")
        try:
            while True:
                try:
                    instr = self.input_data()
                    self.__log.debug("instr=%a", instr)
                except EOFError as _e:
                    print("[EOF]")
                    self.__log.debug(errmsg(_e))
                    break

                # parse
                parsed_data = self.parse_instr(instr)
                self.__log.debug("parsed_data=%s", parsed_data)
                if parsed_data.get("status") != self.RESULT_STATUS["OK"]:
                    self.__log.warning(
                        f"parse error: {parsed_data.get('status')}"
                    )
                    continue

                result_data = {
                    "data": None,
                    "status": self.RESULT_STATUS["ERR"],
                }
                try:
                    # handle and get result
                    result_data = self.handle(parsed_data)
                    self.__log.debug("result_data=%s", result_data)

                    if result_data.get("status") == self.RESULT_STATUS["END"]:
                        raise EOFError(f"{result_data.get('data')}")

                    # output result
                    self.output_result(result_data)

                except EOFError as _e:
                    msg = errmsg(_e)
                    self.__log.warning(msg)
                    raise _e

                except Exception as _e:
                    msg = errmsg(_e)
                    self.__log.warning(msg)

        except KeyboardInterrupt as _e:
            print("^C [Interrupt]")
            self.__log.debug(errmsg(_e))

#
# (c) 2025 Yoichi Tanibayashi
#

from pi0servo import (
    JsonRpcWorker,
    errmsg,
    get_logger,
)


class CmdJsonRpcCli:
    """JSON-RPC CLI."""

    def __init__(self, prompt_str, pi, pins, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("pins=%s", pins)

        self.prompt_str = prompt_str

        self.worker = JsonRpcWorker(pi, pins, debug=self.__debug)

    def end(self):
        """End."""
        self.__log.debug("")
        self.worker.end()
        print("\n* Bye!\n")

    def main(self):
        """Main."""
        self.__log.debug("")

        self.worker.start()

        while True:
            try:
                linestr = input(self.prompt_str)
                self.__log.debug("linestr=%a", linestr)
            except EOFError as e:
                self.__log.debug(errmsg(e))
                break

            ret = self.worker.call(linestr)
            print(ret)

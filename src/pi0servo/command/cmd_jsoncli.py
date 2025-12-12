#
# (c) 2025 Yoichi Tanibayashi
#
import atexit
import json
import os
import readline

from ..helper.thread_worker import ThreadWorker
from ..utils.mylogger import errmsg, get_logger


class CmdJsonCli:
    """JSON(JSON-RPC format) CLI."""

    HIST_LEN = 1000

    def __init__(
        self,
        prompt_str,
        pi,
        pins: list[int],
        history_file: str,
        flag_verbose: bool = False,
        debug: bool = False,
    ) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "prompt_str=%a,pins=%s,history_file=%a,flag_verbose=%s",
            prompt_str,
            pins,
            history_file,
            flag_verbose,
        )

        self.prompt_str = prompt_str
        self.flag_verbose = flag_verbose

        if history_file:
            self.history_file = history_file
        else:
            self.history_file = f"/tmp/hist_{self.__class__.__name__}"
        self.history_file = os.path.expanduser(
            os.path.expandvars(self.history_file)
        )
        self.__log.debug("history_file=%a", self.history_file)

        try:
            readline.read_history_file(self.history_file)
        except Exception as e:
            self.__log.warning(errmsg(e))
        atexit.register(readline.write_history_file, self.history_file)
        readline.set_history_length(self.HIST_LEN)

        self.worker = ThreadWorker(
            pi, pins, flag_verbose=self.flag_verbose, debug=self.__debug
        )

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

            req = []
            try:
                req = json.loads(linestr)
                if isinstance(req, dict):
                    req = [req]
            except Exception as e:
                self.__log.error("%s .. ignored", errmsg(e))
                continue

            ret = self.worker.call(req)
            print(f"ret = {json.dumps(ret, indent=2)}")

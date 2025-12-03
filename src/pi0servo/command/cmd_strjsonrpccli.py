#
# (c) 2025 Yoichi Tanibayashi
#
import atexit
import os
import readline

from pi0servo import JsonRpcWorker, errmsg, get_logger

from ..helper.str_cmd_to_json import StrCmdToJson


class CmdStrJsonRpcCli:
    """JSON-RPC CLI."""

    HIST_LEN = 1000

    def __init__(
        self, prompt_str, pi, pins, history_file, angle_factor, debug=False
    ) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "prompt_str=%a,pins=%s,history_file=%a,angle_factor=%s",
            prompt_str,
            pins,
            history_file,
            angle_factor,
        )

        self.prompt_str = prompt_str

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

        self.parser = StrCmdToJson(angle_factor, debug=self.__debug)
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

            except Exception as e:
                self.__log.error(errmsg(e))
                break

            if not linestr:
                continue

            jsonrpcstr = self.parser.cmdstr_to_jsonliststr(linestr)
            self.__log.debug("jsonrpcstr=%a", jsonrpcstr)

            ret = self.worker.call(jsonrpcstr)
            print(ret)

#
# (c) 2025 Yoichi Tanibayashi
#
"""CLI base"""
import os
import readline

from pi0servo import get_logger


class CliBase:
    """CLI base class"""

    PROMPT_STR = "> "
    COMMENT_STR = "#"
    SPECIAL_COMMAND_PREFIX = "/"

    HIST_LEN = 500

    def __init__(
        self, prompt_prefix, history_file, debug=False
    ):
        """Contractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "prompt_prefix=%s, history_file=%s",
            prompt_prefix, history_file
        )

        self.prompt_prefix = prompt_prefix
        self.history_file = (
            os.path.expanduser(os.path.expandvars(history_file))
        )
        self.__log.debug("history_file=%a", self.history_file)

        try:
            readline.read_history_file(self.history_file)
            readline.set_history_length(self.HIST_LEN)
            _hist_len = readline.get_history_length()
            self.__log.debug("hist_len=%s", _hist_len)
            _cur_hist_len = readline.get_current_history_length()
            self.__log.debug("cur_hist_len=%s", _cur_hist_len)
        except FileNotFoundError:
            self.__log.debug("no history file: %s", self.history_file)
        except OSError:
            self.__log.warning(
                "invalid history file .. remove: %s", self.history_file
            )
            # ヒストリーファイルが壊れていると思うので、削除する。
            os.remove(self.history_file)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def send(self, line):
        """Send.

        To be override.
        """
        self.__log.debug("line=%a", line)

    def parse_line(self, line: str) -> str:
        """Parse line.

        To be override.
        """
        self.__log.debug("line=%a", line)
        return line

    def handle_special(self, line: str):
        """Handle special command."""
        self.__log.debug("line=%a", line)

        self.__log.info("WIP: macro etc.")

        return

    def loop(self):
        """loop"""
        try:
            while True:
                try:
                    _line = input(self.prompt_prefix + self.PROMPT_STR)
                    _line = _line.strip()
                    self.__log.debug("line=%a", _line)
                    # readline.write_history_file(self.history_file)

                except (KeyboardInterrupt, EOFError) as _e:
                    self.__log.debug("%s: %s", type(_e).__name__, _e)
                    break
                except Exception as _e:
                    self.__log.error("%s: %s", type(_e).__name__, _e)
                    continue

                if not _line:
                    continue

                if _line.startswith(self.COMMENT_STR):
                    self.__log.debug("comment line: ignored")
                    continue

                if _line.startswith(self.SPECIAL_COMMAND_PREFIX):
                    # Special command
                    self.handle_special(_line)
                    continue

                try:
                    _parsed_line = self.parse_line(_line)
                    self.__log.debug("parsed_line=%a", _parsed_line)
                    self.send(_parsed_line)

                except Exception as _e:
                    self.__log.warning("%s: %s", type(_e).__name__, _e)

        except (KeyboardInterrupt, EOFError) as _e:
            self.__log.debug("%s: %s", type(_e).__name__, _e)

        finally:
            self.__log.debug("save history: %s", self.history_file)
            try:
                readline.write_history_file(self.history_file)
            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)


# for simple test
def main():
    """test main"""

    class MyCli(CliBase):
        def send(self, line):
            print(f">>> {line}")

        def parse_line(self, line):
            return f"*** {line} ***"

    cli = MyCli("test", "/tmp/hist", debug=True)

    cli.loop()


if __name__ == "__main__":
    main()

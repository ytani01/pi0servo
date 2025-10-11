import blessed
import click
import pigpio
from pyclickutils import click_common_opts, errmsg, get_logger

from pi0servo import StrCmdToJson, ThreadWorker

VERSION_STR = "0.0.1"


class OneKeyCli:
    """One key CLI sample."""

    KEY_BIND = {
        "d": "ms:.1 mr:10,0",
        "f": "ms:.1 mr:-10,0",
        "k": "ms:.1 mr:0,10",
        "j": "ms:.1 mr:0,-10",
        "h": "ms:.1 mv:0,0",
        "q": "QUIT",
        "Q": "QUIT",
        "KEY_ESCAPE": "QUIT",
        "\x04": "QUIT",
    }

    def __init__(self, pi, pins, anglefactor_str: str, debug=False):
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "pi=%s, pins=%s, anglefactor_str=%a", pi, pins, anglefactor_str
        )

        self.pi = pi
        self.pins = pins

        self.angle_factor = self.str_to_anglefactor(anglefactor_str)
        self.__log.debug("angle_factor=%s", self.angle_factor)

        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)
        self.thr_worker = ThreadWorker(self.pi, self.pins, debug=self.__debug)
        self.term = blessed.Terminal()
        self.running = False

    def str_to_anglefactor(self, af_str: str) -> list[int]:
        """String to angle factor."""
        self.__log.debug("af-str=%a", af_str)

        if not af_str:
            return [1] * len(self.pins)

        af = []
        try:
            af = [int(a) for a in af_str.split(",")]
        except Exception as _e:
            self.__log.error(errmsg(_e))
            raise _e

        if len(af) != len(self.pins):
            raise ValueError(f"invalid angle_factor: {af_str!r}")

        return af

    def start(self):
        """Start."""
        self.__log.debug("")
        self.running = True
        self.thr_worker.start()

    def end(self):
        """End."""
        self.__log.debug("")
        self.thr_worker.end()
        self.running = False

    def func_quit(self):
        print("\n=== QUIT ===\n")
        self.end()

    def send_strcmd(self, strcmd):
        print(strcmd)
        jsoncmdlist = self.parser.cmdstr_to_jsonlist(strcmd)
        for jsoncmd in jsoncmdlist:
            self.thr_worker.send(jsoncmd)

    def main(self):
        """Main loop."""
        self.__log.debug("")

        self.start()

        while self.running:
            inkey = ""
            try:
                with self.term.cbreak():
                    inkey = self.term.inkey()
                    self.__log.debug("inkey=%a", inkey)

            except KeyboardInterrupt as _e:
                self.__log.warning("%s: %s", type(_e).__name__, _e)
                break
            except Exception as _e:
                self.__log.warning("%s: %s", type(_e).__name__, _e)
                break

            if not inkey:
                continue

            if inkey.is_sequence:
                inkey_str = inkey.name
            else:
                inkey_str = str(inkey)
            self.__log.debug("inkey_str=%a", inkey_str)
            if not inkey_str:
                continue

            strcmd = self.KEY_BIND.get(inkey_str)
            self.__log.debug("strcmd=%a", strcmd)

            if strcmd:
                if strcmd == "QUIT":
                    self.func_quit()
                else:
                    self.send_strcmd(strcmd)

        self.end()


@click.command()
@click.argument("pins", type=int, nargs=-1)
@click.option(
    "--anglefactor",
    "-a",
    type=str,
    default="",
    help="angle factor: e.g.'-1,1'",
)
@click_common_opts(VERSION_STR)
def main(ctx, pins, anglefactor, debug):
    """Main."""
    command_name = ctx.command.name
    __log = get_logger(command_name, debug)
    __log.debug("command_name=%s", command_name)
    __log.debug("pins=%s, anglefactor=%a", pins, anglefactor)

    if not pins:
        print(ctx.get_help())
        return

    pi = None
    app = None
    try:
        pi = pigpio.pi()
        app = OneKeyCli(pi, pins, anglefactor, debug=debug)
        app.main()
    except Exception as _e:
        msg = errmsg(_e)
        __log.error(msg)
        print(ctx.get_help())
    finally:
        if app:
            app.end()
        if pi:
            pi.stop()


if __name__ == "__main__":
    main()

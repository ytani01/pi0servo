import blessed
import click
import pigpio
from pyclickutils import click_common_opts, errmsg, get_logger

from pi0servo import MultiServo, StrCmdToJson, ThreadWorker

VERSION_STR = "0.0.1"


class OneKeyCli:
    """One key CLI sample."""

    def __init__(self, pi, pins, anglefactor_str: str, debug=False):
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "pi=%s, pins=%s, anglefactor_str=%a", pi, pins, anglefactor_str
        )

        self.pi = pi
        self.pins = pins

        self.angle_factor = None
        try:
            self.angle_factor = [int(a) for a in anglefactor_str.split(",")]
            self.__log.debug("angle_factor=%s", self.angle_factor)
        except Exception as _e:
            msg = errmsg(_e)
            self.__log.error(msg)
            raise _e
        if not self.angle_factor or len(self.angle_factor) != len(self.pins):
            raise ValueError(f"invalid angle_factor: {anglefactor_str!r}")
        self.__log.debug("angle_factor=%a", self.angle_factor)

        self.mservo = MultiServo(self.pi, self.pins, debug=self.__debug)
        self.thr_worker = ThreadWorker(self.mservo, debug=self.__debug)
        self.parser = StrCmdToJson(self.angle_factor, debug=self.__debug)

        self.term = blessed.Terminal()
        self.running = False
        self.keybind = self.setup_keybind()

    def setup_keybind(self):
        """Setup Key bindings."""
        return {
            "d": self.func_left_up,
            "k": self.func_right_up,
            "h": self.func_home,
            "q": self.func_quit,
            "Q": lambda: self.end(),
        }

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

    def func_home(self):
        self.send_strcmd("ms:.2 mv:0,0")

    def func_left_up(self):
        self.send_strcmd("ms:.1 mr:10,0")

    def func_right_up(self):
        self.send_strcmd("ms:.1 mr:0,10")

    def main(self):
        """Main loop."""
        self.__log.debug("")

        self.start()

        with self.term.cbreak():
            while self.running:
                inkey = ""
                try:
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

                action = self.keybind.get(inkey_str)

                if action:
                    action()

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

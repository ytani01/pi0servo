#
# (c) 2025 Yoichi Tanibayashi
#
from ..utils.mylogger import errmsg, get_logger


class CmdLib:
    """common functions for commands."""

    ERR_PIN = -999
    ERR_ANGLE_FACTOR = 0

    def __init__(self, debug=False):
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

    def parse_pinsstr(self, pins_str: str):
        """Parse pins string.

        "22,27-" --> pins = [22,27], angle_factors = [1, -1]
        """
        self.__log.debug("pins_str=%s", pins_str)

        pins = []
        angle_factors = []
        for p in pins_str.split(","):
            p = p.strip()
            try:
                if p[-1] == "-":
                    pins.append(int(p[:-1]))
                    angle_factors.append(-1)
                else:
                    pins.append(int(p))
                    angle_factors.append(1)
            except ValueError as e:
                self.__log.warning(errmsg(e))
                pins.append(self.ERR_PIN)
                angle_factors.append(self.ERR_ANGLE_FACTOR)

        self.__log.debug("pins=%s, angle_factors=%s", pins, angle_factors)

        return pins, angle_factors

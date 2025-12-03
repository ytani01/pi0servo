#
# (c) 2025 Yoichi Tanibayashi
#
from ..utils.mylogger import errmsg, get_logger


class CommonLib:
    """common functions for commands."""

    ERR_PIN = -999
    ERR_ANGLE_FACTOR = 0

    def __init__(self, debug=False):
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

    def parse_pins_str(self, pins_str: str):
        """Parse pins string.

        Args:
            pins_str (str):

        Returns:
            pins (list[int]):
            angle_factor (list[int]):

        Examples:
            "22,27-" --> [22, 27], [1, -1]
            "aaa, bbb" --> [], []
        """
        self.__log.debug("pins_str=%a", pins_str)

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
                #
                # 一部分のエラーでも、全体をエラーとする。
                #
                # pins.append(self.ERR_PIN)
                # angle_factors.append(self.ERR_ANGLE_FACTOR)
                return [], []

        self.__log.debug("pins=%s, angle_factors=%s", pins, angle_factors)

        return pins, angle_factors

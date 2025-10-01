#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_apiserver.py"""

import os

import uvicorn
from pyclickutils import get_logger


class CmdApiServer:
    """API Server command."""

    ENV_PINS = "PI0SERVO_PINS"
    ENV_DEBUG = "PI0SERVO_DEBUG"

    MODULE_API = "pi0servo.web.json_api:app"

    def __init__(self, pins, hostname, port, debug=False):
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(__class__.__name__, self.__debug)
        self.__log.debug("pin=%s", pins)
        self.__log.debug("hostname=%s, port=%s", hostname, port)

        self.pins = pins
        self.hostname = hostname
        self.port = port

    def main(self):
        """main."""
        self.__log.debug("")

        os.environ[self.ENV_PINS] = ",".join([str(p) for p in self.pins])
        os.environ[self.ENV_DEBUG] = "1" if self.__debug else "0"

        uvicorn.run(
            self.MODULE_API,
            host=self.hostname,
            port=self.port,
            reload=True,
            log_level="debug" if self.__debug else "warning",
        )

    def end(self):
        """end"""
        self.__log.debug("")

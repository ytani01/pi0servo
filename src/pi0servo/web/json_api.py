#
# (c) 2025 Yoichi Tanibayashi
#
"""pi0servo JSON API Server."""

import json
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Union

import pigpio
from fastapi import Body, FastAPI, Request
from pyclickutils import get_logger

from pi0servo import ThreadWorker


class JsonApi:
    """Main class for Web Application"""

    def __init__(self, pins, debug=False):
        """constractor"""
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.pins = pins

        self.__log.debug("pins=%s", self.pins)

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise ConnectionError("pigpio daemon")

        self.thr_worker = ThreadWorker(self.pi, self.pins, debug=self._debug)
        self.thr_worker.start()
        self.__log.info("Ready")

    def end(self):
        """end"""
        self.thr_worker.end()
        self.__log.info("done")

    def send_cmdjson(self, cmdjson: dict) -> dict:
        """send JSON command to thread worker"""
        self.__log.debug("cmdjson=%s", cmdjson)

        _res: dict = self.thr_worker.send(cmdjson)

        return _res


# --- FastAPI Lifespan Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan manager for the application"""

    # --- get options from envron variables ---
    pins_str = str(os.getenv("PI0SERVO_PINS"))
    pins = [int(p.strip()) for p in pins_str.split(",")]

    debug_str = os.getenv("PI0SERVO_DEBUG", "0")
    debug = debug_str == "1"

    log = get_logger(__name__, debug)
    log.debug("pins=%s, debug=%s", pins, debug)

    app.state.json_app = JsonApi(pins, debug=debug)
    app.state.debug = debug

    yield

    app.state.json_app.end()


# --- make 'app' ---
app = FastAPI(lifespan=lifespan)


# --- API Endpoints ---
@app.get("/")
async def read_root():
    """root"""
    return {"Hello": "World"}


@app.post("/cmd")
async def exec_cmd(
    request: Request,
    cmd: Union[List[Dict[str, Any]], Dict[str, Any]] = Body(),
):
    """execute commands.

    JSON配列を受け取り、コマンドを実行する。
    """
    debug = request.app.state.debug
    _log = get_logger(__name__, debug)
    _log.debug("cmd=%s: %s", cmd, type(cmd).__name__)

    cmd_list: List[Dict[str, Any]]
    if isinstance(cmd, dict):
        cmd_list = [cmd]
    else:
        cmd_list = cmd

    _json_app = request.app.state.json_app
    _res = []
    for c in cmd_list:
        _res1: dict = _json_app.send_cmdjson(c)
        _log.debug("c=%s, _res1=%s", json.dumps(c), json.dumps(_res1))
        _res.append(_res1)

    _log.debug("_res=%s", json.dumps(_res))
    if len(_res) == 1:
        return _res[0]
    return _res

#
# (c) 2025 Yoichi Tanibayashi
#
import json
import queue
import threading
import time

from ..core.multi_servo import MultiServo
from ..utils.my_logger import get_logger


class ThreadWorker(threading.Thread):
    """Thred worker.

    すべてのコマンドは、JSON形式で、キューを介して受け渡される。

    利用者は、コマンドを`send()`したら、ブロックせずに、
    非同期に他の処理を行える。

    `Worker`は、コマンドキューから一つずつコマンドを取り出し、
    順に実行する。

    コマンドをキャンセルしたい場合は、`clear_cmdq()`で、
    キューに溜まっているコマンドをすべてキャンセルできる。
    """

    ERROR_CODE = {
        "INVALID_JSON": -32700,
        "INVALID_REQUEST": -32600,
        "METHOD_NOT_FOUND": -32601,
        "INVALID_PARAM": -32602,
        "INTERNAL_ERROR": -32603,
        "UNKOWN": -32000,
    }

    CMD_CANCEL = "cancel"
    CMD_QSIZE = "qsize"
    CMD_WAIT = "wait"

    # コマンド一覧(例)
    # コマンドチェックにも使う
    CMD_SAMPLES_ALL: list[dict] = [
        {
            "method": "move_all_angles_sync",
            "params": {
                "angles": [30, None, "center"],
                "move_sec": 0.2,
                "step_n": 40
            }
        },
        {
            "method": "move",
            "params": {
                "angles": [30, None, "center"],
                "move_sec": 0.2,
                "step_n": 40
            }
        },
        {
            "method": "move_all_angles",
            "params": {
                "angles": [30, None, "center"]
            }
        },
        {
            "method": "move_all_pulses",
            "params": {
                "pulses": [1000, 2000, None, 0]
            }
        },
        {
            "method": "move_sec",
            "params": {
                "sec": 1.5
            }
        },
        {
            "method": "step_n",
            "params": {
                "n": 40
            }
        },
        {
            "method": "interval",
            "params": {
                "sec": 0.5
            }
        },
        {
            "method": "sleep",
            "params": {
                "sec": 1.0
            }
        },
        {
            "method": "move_pulse_relative",
            "params": {
                "servo": 2,
                "pulse_diff": -20
            }
        },
        {
            "method": "set",
            "params": {
                "servo": 1,
                "target": "center"
            }
        },
        {
            "method": CMD_CANCEL,
            "params": {
                "comment": "special command"
            }
        },
        {
            "method": CMD_QSIZE,
            "params": {
                "comment": "special command"
            }
        },
        {
            "method": CMD_WAIT,
            "params": {
                "comment": "special command"
            }
        },
    ]

    DEF_RECV_TIMEOUT = 0.2  # sec
    DEF_INTERVAL_SEC = 0.0  # sec

    def __init__(
        self,
        mservo: MultiServo,
        move_sec: float | None = None,
        step_n: int | None = None,
        interval_sec: float = DEF_INTERVAL_SEC,
        debug=False,
    ):
        """Constructor."""
        super().__init__(daemon=True)

        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)

        self.mservo = mservo

        if move_sec is None:
            self.move_sec = mservo.DEF_MOVE_SEC
        else:
            self.move_sec = move_sec

        if step_n is None:
            self.step_n = mservo.DEF_STEP_N
        else:
            self.step_n = step_n

        self.interval_sec = interval_sec

        self.__log.debug(
            "move_sec=%s, step_n=%s, interval_sec=%s",
            move_sec, step_n, interval_sec
        )

        self._cmdq: queue.Queue = queue.Queue()
        self._active = False
        self._busy_flag = False

        self._cmd_list = []
        for _c in self.CMD_SAMPLES_ALL:
            self._cmd_list.append(_c.get("method"))
        self.__log.debug("cmd_list=%s", self._cmd_list)

        self._command_handlers = {
            "move": self._handle_move_all_angles_sync,
            "move_all_angles_sync": self._handle_move_all_angles_sync,
            "move_all_angles": self._handle_move_all_angles,
            "move_all_pulses": self._handle_move_all_pulses,
            "move_sec": self._handle_move_sec,
            "step_n": self._handle_step_n,
            "interval": self._handle_interval,
            "sleep": self._handle_sleep,
            "move_pulse_relative": self._handle_move_pulse_relative,
            "set": self._handle_set,
        }

    @property
    def qsize(self) -> int:
        """Size of command queue."""
        return self._cmdq.qsize()

    def __del__(self):
        """del"""
        self._active = False
        self.__log.debug("")

    def end(self):
        """end worker"""
        self.__log.debug("")
        self._active = False
        self.clear_cmdq()
        self.join()
        self.__log.debug("done")

    def clear_cmdq(self):
        """clear command queue"""
        _count = 0
        while not self._cmdq.empty():
            _count += 1
            _cmd = self._cmdq.get()
            self.__log.debug("%2d:%s", _count, _cmd)

        self.__log.debug("count=%s", _count)
        return _count

    def mk_reply_result(
        self, result: int | str | dict | None, req: str | dict
    ) -> str:
        """Make reply JSON string."""
        self.__log.debug("result=%s", result)

        reply = {
            "result": {
                "value": result,
                "qsize": self.qsize,
                "busy_flag": self._busy_flag,
                "request": req
            }
        }
        self.__log.debug("reply=%s", reply)
        return json.dumps(reply)

    def mk_reply_error(self, code_key: str, message: str, data=None) -> str:
        """Make error reply JSON string."""
        self.__log.debug(
            "code_key=%s, message=%s, data=%s", code_key, message, data
        )

        reply = {
            "error": {
                "code": self.ERROR_CODE[code_key],
                "message": message,
            }
        }
        if data:
            reply["error"]["data"] = data

        self.__log.debug("reply=%s", reply)
        return json.dumps(reply)

    def send(self, cmd_data: str | dict):
        """Send cmd_data(JSON)"""
        try:
            if isinstance(cmd_data, str):
                cmd_json = json.loads(cmd_data)
            else:
                cmd_json = cmd_data

            # 最初にエラーキーチェック
            error_key = cmd_json.get("error")
            if error_key:
                _ret = self.mk_reply_error(
                    error_key, error_key, cmd_json.get("data")
                )
                return _ret

            # コマンド名チェック
            cmd_name = cmd_json.get("method")
            if cmd_name is None:
                err_msg = "Not a command"
                _ret = self.mk_reply_error("INVALID_JSON", err_msg, cmd_json)
                self.__log.debug("_ret=%s", _ret)
                return _ret

            if cmd_name not in self._cmd_list:
                err_msg = f"Invalid command: {cmd_name}"
                _ret = self.mk_reply_error(
                    "METHOD_NOT_FOUND", err_msg, cmd_json
                )
                self.__log.debug("_ret=%s", _ret)
                return _ret

            if cmd_name == self.CMD_CANCEL:
                _count = self.clear_cmdq()
                _ret = self.mk_reply_result(_count, cmd_data)
                self.__log.debug("_ret=%s", _ret)
                return _ret

            if cmd_name == self.CMD_QSIZE:
                _ret = self.mk_reply_result(self.qsize, cmd_data)
                self.__log.debug("_ret=%s", _ret)
                return _ret

            if cmd_name == self.CMD_WAIT:
                while self._busy_flag or self.qsize > 0:
                    self.__log.debug("waiting..")
                    time.sleep(0.5)
                _ret = self.mk_reply_result(self.qsize, cmd_data)
                self.__log.debug("done")
                return _ret

            # 通常のコマンドは、コマンドキューに入れる。
            self._cmdq.put(cmd_json)

            self.__log.debug(
                "cmd_json=%s, qsize=%s", cmd_json, self._cmdq.qsize()
            )

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

        _ret = self.mk_reply_result(None, cmd_data)
        return _ret

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """Receive command form queue."""
        try:
            _cmd_data = self._cmdq.get(timeout=timeout)
        except queue.Empty:
            _cmd_data = ""

        return _cmd_data

    def _handle_move_all_angles_sync(self, cmd: dict):
        """Handle move_all_angles_sync().

        e.g.
        {
          "method": "move_all_angles_sync",
          "params:": {
            "angles": [30, None, -30, 0],
            "move_sec": 0.2,  # optional
            "step_n": 40  # optional
          }
        }
        """
        try:
            _params: dict = cmd["params"]
            _angles = _params["angles"]
            _move_sec = _params.get("move_sec")
            if _move_sec is None:
                _move_sec = self.move_sec
            _step_n = _params.get("step_n")
            if _step_n is None:
                _step_n = self.step_n

        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_all_angles_sync(_angles, _move_sec, _step_n)
        self._sleep_interval()

    def _handle_move_all_angles_sync_relative(self, cmd: dict):
        """Handle move_all_angles_sync_relative().

        e.g.
        {
          "method": "move_all_angles_sync_relative",
          "params": {
            "angle_diffs": [10, -10, 0, 0],
            "move_sec": 0.2,  # optional
            "step_n": 40  # optional
          }
        }
        """
        try:
            _params = cmd["params"]
            _angle_diffs = _params["angle_diffs"]
            _move_sec = _params["move_sec"]
            if _move_sec is None:
                _move_sec = self.move_sec
            _step_n = _params.get("step_n")
            if _step_n is None:
                _step_n = self.step_n
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_all_angles_sync_relative(
            _angle_diffs, _move_sec, _step_n
        )
        self._sleep_interval()

    def _handle_move_all_angles(self, cmd: dict):
        """Handle move_all_angles().

        e.g.
        {
          "method": "move_all_angles",
          "params": {
            "angles": [30, None, -30, 0]
          }
        }
        """
        try:
            _params = cmd["params"]
            _angles = _params["angles"]
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_all_angles(_angles)
        self._sleep_interval()

    def _handle_move_all_pulses(self, cmd: dict):
        """Handle move_all_pulses().

        e.g.
        {
          "method": "move_all_pulses",
          "params": {
            "pulses": [2000, 1000, None, 0]
          }
        }
        """
        try:
            _params = cmd["params"]
            _pulses = _params["pulses"]
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_all_pulses(_pulses)
        self._sleep_interval()

    def _handle_move_all_pulses_relative(self, cmd: dict):
        """Handle move_all_angles().

        e.g.
        {
          "method": "move_all_pulses_relative",
          "params": {
            "pulse_diffs": [2000, 1000, None, 0]
          }
        }
        """
        try:
            _params = cmd["params"]
            _pulse_diffs = _params["pulse_diffs"]
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_all_pulses_relative(_pulse_diffs, forced=True)
        self._sleep_interval()

    def _handle_move_sec(self, cmd: dict):
        """Handle move_sec.

        e.g.
        {
          "method": "move_sec",
          "params": {
            "sec": 1.5
          }
        }
        """
        try:
            _params = cmd["params"]
            self.move_sec = float(_params["sec"])
            self.__log.debug("move_sec=%s", self.move_sec)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def _handle_step_n(self, cmd: dict):
        """Handle step_n.

        e.g.
        {
          "method": "step_n",
          "params": {
            "n": 40
          }
        }
        """
        try:
            _params = cmd["params"]
            self.step_n = int(_params["n"])
            self.__log.debug("step_n=%s", self.step_n)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def _handle_interval(self, cmd: dict):
        """Handle interval.

        e.g.
        {
          "method": "interval",
          "params": {
            "sec": 0.5
          }
        }
        """
        try:
            _params = cmd["params"]
            self.interval_sec = float(_params["sec"])
            self.__log.debug("set interval_sec=%s", self.interval_sec)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def _handle_sleep(self, cmd: dict):
        """Handle sleep.

        e.g.
        {
          "method": "sleep",
          "params": {
            "sec": 1.0
          }
        }
        """
        try:
            _params = cmd["params"]
            _sec = float(_params["sec"])
            self.__log.debug("sleep: %s sec", _sec)
            if _sec > 0.0:
                time.sleep(_sec)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)

    def _sleep_interval(self):
        """sleep interval"""
        if self.interval_sec > 0:
            self.__log.debug("sleep interval_sec: %s sec", self.interval_sec)
            time.sleep(self.interval_sec)

    def _handle_move_pulse_relative(self, cmd: dict):
        """Handle move pulse relative.

        e.g.
        {
          "method": "move_pulse_relative",
          "params": {
            "servo": 2, "pulse_diff": -20
          }
        }
        """
        try:
            _params = cmd["params"]
            servo = int(_params["servo"])
            pulse_diff = int(_params["pulse_diff"])
            self.__log.debug("servo=%s, pulse_diff=%s", servo, pulse_diff)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        self.mservo.move_pulse_relative(servo, pulse_diff, forced=True)

    def _handle_set(self, cmd: dict):
        """Handle set cmd. (save calibration)

        e.g.
        {
          "method": "set",
          "params": {
            "servo": 1,
            "target": "max"
          }
        }

        * pulse is current value.
        """
        try:
            _params = cmd["params"]
            _servo = int(_params["servo"])
            _target = _params["target"]
            self.__log.debug("set: servo:%s", _servo)
        except Exception as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return

        if _target == "center":
            self.mservo.set_pulse_center(_servo)
        elif _target == "min":
            self.mservo.set_pulse_min(_servo)
        elif _target == "max":
            self.mservo.set_pulse_max(_servo)
        else:
            self.__log.warning("Invalid target: %s", _target)

    def _dispatch_cmd(self, cmd_data: dict):
        """Dispatch command."""
        self.__log.debug("cmd_data=%a", cmd_data)

        _cmd_str = cmd_data.get("method")
        if not _cmd_str:
            self.__log.error("invalid command (no 'method'): %s", cmd_data)
            return

        handler = self._command_handlers.get(_cmd_str)
        if handler:
            handler(cmd_data)
        else:
            self.__log.error("unknown command: %s", cmd_data)

    def run(self):
        """run"""
        self.__log.debug("start")

        self._active = True

        while self._active:
            if self.qsize == 0:
                self._busy_flag = False
            _cmd_data = self.recv()
            if not _cmd_data:
                continue
            self._busy_flag = True

            self.__log.debug("qsize=%s", self._cmdq.qsize())
            try:
                self._dispatch_cmd(_cmd_data)

            except Exception as _e:
                self.__log.error("%s: %s", type(_e).__name__, _e)

        self.__log.debug("done")

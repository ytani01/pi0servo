#
# (c) 2025 Yoichi Tanibayashi
#
import json
import queue
import threading
import time

from jsonrpc import Dispatcher, JSONRPCResponseManager

from ..core.calibrable_servo import CalibrableServo
from ..core.multi_servo import MultiServo
from ..utils.mylogger import errmsg, get_logger


class HandleCall:
    """Functions for call."""

    RESULT_QUEUE = "queue"

    def __init__(self, cmdq: queue.Queue, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

        self.cmdq = cmdq

    def _clear_cmdq(self):
        """Clear command queue."""
        _count = 0
        while not self.cmdq.empty():
            _count += 1
            _cmd = self.cmdq.get()
            self.__log.debug("%2d:%s", _count, _cmd)

        self.__log.debug("count=%s", _count)
        return _count

    def cancel(self) -> int:
        self.__log.debug("")
        return self._clear_cmdq()

    def qsize(self) -> int:
        self.__log.debug("")
        return self.cmdq.qsize()

    def wait(self):
        self.__log.debug("qsize=%s", self.cmdq.qsize())
        return True

    def move_all_angles_sync(self, angles: list[float]):
        self.__log.debug("angles=%s", angles)
        return self.RESULT_QUEUE

    def move_all_angles_sync_relative(self, angle_diffs: list[float]):
        """Move all angles sync."""
        self.__log.info("angle_diffs=%s", angle_diffs)
        return self.RESULT_QUEUE


class HandleExec:
    """Functions for exec."""

    def __init__(self, mservo: MultiServo, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

        self.mservo = mservo

    def move_all_angles_sync(self, angles: list[float]):
        """Move all angles sync."""
        self.__log.info("angles=%s", angles)
        self.mservo.move_all_angles_sync(angles)

    def move_all_angles_sync_relative(self, angle_diffs: list[float]):
        """Move all angles sync."""
        self.__log.info("angle_diffs=%s", angle_diffs)
        self.mservo.move_all_angles_sync_relative(angle_diffs)


class JsonRpcWorker(threading.Thread):
    """JSON RPC Worker."""

    DEF_RECV_TIMEOUT = 0.2  # sec
    DEF_INTERVAL_SEC = 0.0  # sec

    def __init__(
        self,
        pi,
        pins: list[int],
        first_move=True,
        conf_file=CalibrableServo.DEF_CONF_FILE,
        debug=False,
    ) -> None:
        """Constructor."""
        super().__init__(daemon=True)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("pins=%s", pins)

        self.mservo = MultiServo(
            pi, pins, first_move, conf_file, debug=self.__debug
        )

        self.cmdq: queue.Queue = queue.Queue()

        # dispacher for call
        self.obj_call = HandleCall(self.cmdq, debug=self.__debug)
        self.dispacher_call = Dispatcher()
        self.dispacher_call.add_object(self.obj_call)

        # dispacher for exec
        self.obj_exec = HandleExec(self.mservo, debug=self.__debug)
        self.dispacher_exec = Dispatcher()
        self.dispacher_exec.add_object(self.obj_exec)
        self.exec_class_name = self.obj_exec.__class__.__name__.lower()

        # flags
        self._flag_active = False
        self._flag_busy = False

        # default parameters
        self.move_sec = MultiServo.DEF_MOVE_SEC
        self.step_n = MultiServo.DEF_STEP_N
        self.interval_sec = self.DEF_INTERVAL_SEC

        # JSON-RPC ID
        self.rpc_id: int = 0

    def end(self):
        """End."""
        self.__log.debug("")

        # stop thread
        self._flag_active = False
        self.clear_cmdq()
        self.join()

        # off all servo
        self.mservo.off()

        self.__log.debug("done")

    def __enter__(self):
        """Enter for 'with'."""
        self.__log.debug("")
        self.start()
        return self

    def __exit__(self, ex_type, ex_value, trace):
        """Exit for 'with'."""
        self.__log.debug(
            "ex_type=%s, ex_value=%s, trace=%s", ex_type, ex_value, trace
        )
        if ex_type:
            self.__log.error("%s: %s", ex_type.__name__, ex_value)
            return True

        self.end()
        return False

    @property
    def qsize(self) -> int:
        """Size of command queue."""
        return self.cmdq.qsize()

    def __del__(self):
        """Delete."""
        self._active = False
        self.__log.debug("")

    def clear_cmdq(self):
        """Clear command queue."""
        _count = 0
        while not self.cmdq.empty():
            _count += 1
            _cmd = self.cmdq.get()
            self.__log.debug("%2d:%s", _count, _cmd)

        self.__log.debug("count=%s", _count)
        return _count

    def mk_jsonrpc_req(self, cmd: str | dict, prefix="") -> str:
        """Make JSON-RPC request."""
        self.__log.debug("cmd=%s", cmd)

        _cmdstr = ""
        _cmddict = {}
        try:
            if isinstance(cmd, str):
                _cmdstr = cmd
                _cmddict = json.loads(cmd)
            else:  # dict
                _cmdstr = json.dumps(cmd)
                _cmddict = cmd

            if prefix:
                _cmddict["method"] = f"{prefix}.{_cmddict['method']}"

            _id = _cmddict.get("id")
            if isinstance(_id, int):
                self.rpc_id = _id
            else:
                self.rpc_id += 1

            _cmddict["jsonrpc"] = "2.0"
            _cmddict["id"] = self.rpc_id

            _cmdstr = json.dumps(_cmddict)

        except Exception as e:
            self.__log.error(errmsg(e))
            return ""

        return _cmdstr

    def call(self, cmd: str | dict) -> dict:
        """Call(JSON-RPC)."""
        self.__log.debug("cmd=%s", cmd)

        _cmd_jsonstr = self.mk_jsonrpc_req(
            cmd, self.obj_call.__class__.__name__.lower()
        )
        self.__log.debug("_cmd_jsonstr=%a", _cmd_jsonstr)

        # コマンドごとの処理
        # キューに入れない特別な処理を先に行う
        _ret = JSONRPCResponseManager.handle(
            _cmd_jsonstr, self.dispacher_call
        )
        if _ret is None:
            self.__log.warning("_ret=%s", _ret)
            return {"error": "_ret is None"}

        if not isinstance(_ret.data, dict):
            self.__log.warning("_ret.data=%s", _ret.data)
            return {"error": f"_ret.data={_ret.data}"}

        self.__log.debug("ret.data=%s", _ret.data)

        _result = _ret.data.get("result")
        if _result is None:
            return {"error": "_result is None"}

        if _result != HandleCall.RESULT_QUEUE:
            # キューに入れないコマンドを正常実行した。
            return _ret.data

        # 通常のコマンドは、コマンドキューに入れ、
        # 実行を HandleExec クラスに委ねる。
        # このとき、メソッド名を変換する。
        try:
            # メソッド名 "handlecall.foo" -> "handleexec.foo"
            _cmd_dict = json.loads(_cmd_jsonstr)
            _method_name = _cmd_dict["method"]
            _method_name = _method_name.split(".")[1]
            self.__log.debug("_method_name=%a", _method_name)

            _cmd_dict["method"] = f"{self.exec_class_name}.{_method_name}"
            _cmd_jsonstr = json.dumps(_cmd_dict)
            self.__log.debug("_cmd_jsonstr=%a", _cmd_jsonstr)

        except Exception as _e:
            _msg = errmsg(_e)
            self.__log.error(_msg)
            return {"error": _msg}

        self.cmdq.put(_cmd_jsonstr)
        self.__log.debug(
            "_cmd_jsonstr=%a, qsize=%s", _cmd_jsonstr, self.qsize
        )
        return {"result": True, "qsize": self.qsize, "cmd": _cmd_jsonstr}

    def recv(self, timeout=DEF_RECV_TIMEOUT):
        """Receive command form queue."""
        try:
            _cmd_data = self.cmdq.get(timeout=timeout)
        except queue.Empty:
            _cmd_data = ""

        return _cmd_data

    def run(self):
        """Run."""
        self.__log.debug("")

        self._flag_active = True

        while self._flag_active:
            if self.qsize == 0:
                self._flag_busy = False

            _cmd_data = self.recv()
            if not _cmd_data:
                continue

            self._flag_busy = True

            self.__log.debug("_cmd_data=%a, qsize=%s", _cmd_data, self.qsize)

            ret = None
            try:
                ret = JSONRPCResponseManager.handle(
                    _cmd_data, self.dispacher_exec
                )
            except Exception as e:
                self.__log.error(errmsg(e))

            if ret:
                self.__log.debug("ret.data=%s", ret.data)

                if self.interval_sec > 0.0:
                    time.sleep(self.interval_sec)

        self.__log.debug("done.")

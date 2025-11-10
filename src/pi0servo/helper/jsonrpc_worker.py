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

    def move_all_angles_sync(
        self,
        angles: list[float],
        move_sec: float | None = None,
        step_n: int | None = None,
    ):
        self.__log.info(
            "angles=%s,move_sec=%s,step_n=%s", angles, move_sec, step_n
        )
        return self.RESULT_QUEUE

    def move_all_angles_sync_relative(
        self,
        angle_diffs: list[float],
        move_sec: float | None = None,
        step_n: int | None = None,
    ):
        """Move all angles sync."""
        self.__log.info(
            "angle_diffs=%s,move_sec=%s,step_n=%s",
            angle_diffs,
            move_sec,
            step_n,
        )
        self.__log.debug("angle_diffs=%s", angle_diffs)
        return self.RESULT_QUEUE

    def sleep(self, sec: float):
        """Sleep."""
        self.__log.debug("sec=%s", sec)
        return self.RESULT_QUEUE

    def move_sec(self, sec: float):
        """Set move sec."""
        self.__log.debug("sec=%s", sec)
        return self.RESULT_QUEUE

    def step_n(self, step_n: int):
        """Set number steps."""
        self.__log.debug("step_n=%s", step_n)
        return self.RESULT_QUEUE

    def interval(self, sec: float):
        """Set interval sec."""
        self.__log.debug("sec=%s", sec)
        return self.RESULT_QUEUE


class HandleExec:
    """Functions for exec."""

    def __init__(self, mservo: MultiServo, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

        self.mservo = mservo

        self.param_move_sec = MultiServo.DEF_MOVE_SEC
        self.param_step_n = MultiServo.DEF_STEP_N
        self.param_interval_sec = 0.0

    def move_all_angles_sync(
        self, angles: list[float], move_sec=None, step_n=None
    ):
        """Move all angles sync."""
        self.__log.info(
            "angles=%s,move_sec=%s,step_n=%s", angles, move_sec, step_n
        )
        if move_sec is None:
            move_sec = self.param_move_sec
        if step_n is None:
            step_n = self.param_step_n

        self.mservo.move_all_angles_sync(angles, move_sec, step_n)

        if self.param_interval_sec:
            time.sleep(self.param_interval_sec)

    def move_all_angles_sync_relative(
        self, angle_diffs: list[float], move_sec=None, step_n=None
    ):
        """Move all angles sync."""
        self.__log.info(
            "angle_diffs=%s,move_sec=%s,step_n=%s",
            angle_diffs,
            move_sec,
            step_n,
        )
        if move_sec is None:
            move_sec = self.param_move_sec
        if step_n is None:
            step_n = self.param_step_n

        self.mservo.move_all_angles_sync_relative(angle_diffs)

        if self.param_interval_sec:
            time.sleep(self.param_interval_sec)

    def sleep(self, sec: float):
        """Sleep."""
        self.__log.info("sec=%s", sec)
        time.sleep(sec)

    def move_sec(self, sec: float):
        """Set move sec."""
        self.__log.debug("sec=%s", sec)
        self.param_move_sec = sec

    def step_n(self, step_n: int):
        """Set number steps."""
        self.__log.debug("step_n=%s", step_n)
        self.param_step_n = step_n

    def interval(self, sec: float):
        """Set interval sec."""
        self.__log.debug("sec=%s", sec)
        self.param_interval_sec = sec


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

    def mk_jsonrpc_req(self, cmdstr: str, method_prefix="") -> str:
        """Make JSON-RPC request."""
        self.__log.debug("cmdstr=%s", cmdstr)

        try:
            _cmddata = json.loads(cmdstr)
            if not isinstance(_cmddata, list):
                _cmddata = [_cmddata]  # すべてリストで扱う

            _new_cmddata = []
            for _d in _cmddata:
                if method_prefix:
                    _d["method"] = f"{method_prefix}.{_d['method']}"

                _id = _d.get("id")
                if isinstance(_id, int):
                    self.rpc_id = _id
                    _d["id"] = _id
                else:
                    self.rpc_id += 1
                    _d["id"] = self.rpc_id

                _d["jsonrpc"] = "2.0"

                _new_cmddata.append(_d)

            _cmdstr = json.dumps(_new_cmddata)

        except Exception as e:
            self.__log.error(errmsg(e))
            return ""

        return _cmdstr

    def call(self, cmdstr: str) -> str:
        """Call(JSON-RPC)."""
        self.__log.debug("cmdstr=%s", cmdstr)

        # JSON-RPCリクエスト形式に整える
        _cmd_jsonstr = self.mk_jsonrpc_req(
            cmdstr, self.obj_call.__class__.__name__.lower()
        )
        self.__log.debug("_cmd_jsonstr=%a", _cmd_jsonstr)

        _cmd_jsondata: list[dict] = []
        try:
            _cmd_jsondata = json.loads(_cmd_jsonstr)
            self.__log.debug("_cmd_jsondata=%a", json.dumps(_cmd_jsondata))
        except Exception as _e:
            _msg = errmsg(_e)
            self.__log.error(_msg)
            return _msg

        _exec_cmd_jsondata = []  # キューイングすべきコマンドのリスト
        _result_list = []
        for _j in _cmd_jsondata:
            self.__log.debug("_j=%a", json.dumps(_j))

            # コマンドごとの処理
            # キューに入れない特別な処理を先に行う
            _ret = JSONRPCResponseManager.handle(
                json.dumps(_j), self.dispacher_call
            )
            if _ret is None:
                self.__log.warning("_ret=%s", _ret)
                _result_list.append(f"_ret={_ret}")
                continue

            if not isinstance(_ret.data, dict):
                self.__log.warning("_ret.data=%s", _ret.data)
                _result_list.append(f"_ret.data={_ret.data}")
                continue

            self.__log.debug("ret.data=%s", _ret.data)

            _result = _ret.data.get("result")
            if _result is None:
                self.__log.warning("_result is None")
                _result_list.append("_result is None")
                continue

            if _result != HandleCall.RESULT_QUEUE:
                # キューに入れないコマンドを正常実行した。
                self.__log.debug("_ret.data=%s", _ret.data)
                _result_list.append(_result)
                continue

            # キューイングすべきコマンドの処理
            _result_list.append(_result)
            try:
                # メソッド名 "handlecall.foo" -> "handleexec.foo"
                _method_name = _j["method"].split(".")[1]
                _j["method"] = f"{self.exec_class_name}.{_method_name}"
                self.__log.debug("_j=%a", json.dumps(_j))

                _exec_cmd_jsondata.append(_j)

            except Exception as _e:
                _msg = errmsg(_e)
                self.__log.error(_msg)
                return json.dumps({"error": _msg})

        if _exec_cmd_jsondata:
            self.cmdq.put(_exec_cmd_jsondata)
            self.__log.debug(
                "_exec_cmd_jsondata=%a, qsize=%s",
                json.dumps(_exec_cmd_jsondata),
                self.qsize,
            )

        return json.dumps(_result_list)

    def recv(self, timeout=DEF_RECV_TIMEOUT) -> str:
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
            self.__log.debug("_cmd_data=%a, qsize=%s", _cmd_data, self.qsize)

            self._flag_busy = True

            ret = None
            try:
                _cmd_str = json.dumps(_cmd_data)
                ret = JSONRPCResponseManager.handle(
                    _cmd_str, self.dispacher_exec
                )
            except Exception as e:
                self.__log.error(errmsg(e))

            if ret:
                self.__log.debug("ret.data=%s", ret.data)

                if self.interval_sec > 0.0:
                    time.sleep(self.interval_sec)

        self.__log.debug("done.")

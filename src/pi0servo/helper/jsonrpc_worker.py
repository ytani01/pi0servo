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

    def __init__(self, worker, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

        self.worker = worker

    def cancel(self) -> int:
        """Cancel commands in queue."""
        self.__log.debug("")
        _cancel_count = 0
        while not self.worker.cmdq.empty():
            _cancel_count += 1
            _cmd = self.worker.cmdq.get()
            self.__log.debug("%2d:%s", _cancel_count, _cmd)
        return _cancel_count

    def qsize(self) -> int:
        """Queue size."""
        self.__log.debug("")
        _qsize = self.worker.qsize
        self.__log.debug("_qsize=%s", _qsize)
        return _qsize

    def wait(self, wait_interval: float = 0.5):
        """Wait worker."""
        self.__log.debug(
            "wait_interval=%s,qsize=%s", wait_interval, self.worker.qsize
        )
        while self.worker.is_busy:
            self.__log.debug(
                "waiting worker(busy, qsize=%s)..", self.worker.qsize
            )
            time.sleep(wait_interval)
        return True


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
        self.__log.debug(
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
        self.__log.debug(
            "angle_diffs=%s,move_sec=%s,step_n=%s",
            angle_diffs,
            move_sec,
            step_n,
        )
        if move_sec is None:
            move_sec = self.param_move_sec
        if step_n is None:
            step_n = self.param_step_n

        self.mservo.move_all_angles_sync_relative(
            angle_diffs, move_sec, step_n
        )

        if self.param_interval_sec:
            time.sleep(self.param_interval_sec)

    def sleep(self, sec: float):
        """Sleep."""
        self.__log.debug("sec=%s", sec)
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

    def move_pulse_relative(self, servo_idx: int, pulse_diff: int):
        """Move one servo by relative pulse."""
        self.__log.debug("servo_i=%s,pulse_diff=%s", servo_idx, pulse_diff)
        self.mservo.move_pulse_relative(servo_idx, pulse_diff, forced=True)

    def set(self, servo_i: int, target: str) -> bool:
        """Set calibrated pulse as target."""
        self.__log.debug("servo_i=%s,target=%s", servo_i, target)

        _target = target.lower()

        if _target == "center":
            self.mservo.set_pulse_center(servo_i)
            return True
        if _target == "min":
            self.mservo.set_pulse_min(servo_i)
            return True
        if _target == "max":
            self.mservo.set_pulse_max(servo_i)
            return True

        self.__log.error("Invalid target: %a", target)
        return False


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

        # dispatcher for call
        self.obj_call = HandleCall(self, debug=self.__debug)
        self.obj_call_classname = self.obj_call.__class__.__name__.lower()
        self.dispatcher_call = Dispatcher()
        self.dispatcher_call.add_object(self.obj_call)

        # dispatcher for exec
        self.obj_exec = HandleExec(self.mservo, debug=self.__debug)
        self.obj_exec_classname = self.obj_exec.__class__.__name__.lower()
        self.dispatcher_exec = Dispatcher()
        self.dispatcher_exec.add_object(self.obj_exec)
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

    @property
    def is_busy(self) -> bool:
        """Busy flag."""
        return self._flag_busy

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
        """Make JSON-RPC request.

        Args:
            cmdstr (str):
                '{
                     "method": "aaa.bbb",
                     "params": [a, b]
                 }'
            mothod_prefix (str): "ccc"

        Returns:
            jsonrpc_req_str (str):
                '{
                     "method": "ccc.bbb",
                     "params": [a, b],
                     "jsonrpc": "2.0",
                     "id": 1
                 }'
        """
        self.__log.debug("cmdstr=%a, method_prefix=%a", cmdstr, method_prefix)

        _jsonrpc_req_dict = {
            "jsonrpc": "2.0",
            "method": "",
            "params": [],
            "id": 0,
        }
        try:
            _cmd_dict = json.loads(cmdstr)

            _req_id = _cmd_dict.get("id")
            if _req_id:
                self.rpc_id = _req_id
            else:
                self.rpc_id += 1
            _jsonrpc_req_dict["id"] = self.rpc_id

            _method_name = _cmd_dict["method"]
            if method_prefix:
                _method_name_base = _method_name.split(".")[-1]
                _method_name = f"{method_prefix}.{_method_name_base}"
            _jsonrpc_req_dict["method"] = _method_name

            _req_params = _cmd_dict.get("params")
            if _req_params:
                _jsonrpc_req_dict["params"] = _cmd_dict["params"]

            _jsonrpc_req_str = json.dumps(_jsonrpc_req_dict)
            self.__log.debug("_jsonrpc_req_str=%a", _jsonrpc_req_str)
            return _jsonrpc_req_str

        except Exception as e:
            self.__log.error(errmsg(e))
            return ""

    def call(self, cmdstr: str) -> str:
        """Call(JSON-RPC)."""
        self.__log.debug("cmdstr=%s", cmdstr)

        try:
            # list[dict]に変換
            _cmd_dict_list = json.loads(cmdstr)
            if not isinstance(_cmd_dict_list, list):
                _cmd_dict_list = [_cmd_dict_list]
        except Exception as _e:
            _err_msg = errmsg(_e)
            self.__log.error(_err_msg)
            return _err_msg

        _exec_cmd_jsondata_list = []  # キューイングすべきコマンドのリスト
        _result_list = []
        for _cmd_dict in _cmd_dict_list:
            self.__log.debug("_cmd_dict=%a", _cmd_dict)

            _method_name = f"{self.obj_call_classname}.{_cmd_dict['method']}"
            self.__log.debug("_method_name=%a", _method_name)
            self.__log.debug("dispatcher_call:%s", list(self.dispatcher_call))

            if _method_name in list(self.dispatcher_call):
                #
                # キューに入れない処理
                #

                # JSON-RPCリクエスト形式に整える
                _cmd_jsonstr = self.mk_jsonrpc_req(
                    json.dumps(_cmd_dict),
                    self.obj_call.__class__.__name__.lower(),
                )
                self.__log.debug("_cmd_jsonstr=%a", _cmd_jsonstr)

                # 実行
                _ret = JSONRPCResponseManager.handle(
                    _cmd_jsonstr, self.dispatcher_call
                )
                if _ret is None:
                    # _ret is None !?
                    _msg = "_ret is None"
                    self.__log.warning(_msg)
                    _result_list.append(_msg)
                    continue

                # 結果の処理
                self.__log.debug("_ret.data=%s", _ret.data)
                if isinstance(_ret.data, list):
                    # _ret.data が list !?
                    _msg = f"_ret.data={_ret.data}"
                    self.__log.warning(_msg)
                    _result_list.append(_msg)
                    continue

                _ret_result = _ret.data.get("result")
                self.__log.debug("_ret_result=%s", _ret_result)
                if _ret_result is not None:
                    # 正常に実行された
                    _result_list.append(_ret_result)
                    continue

                # 以下、JSON-RPCエラーの場合
                _ret_err = _ret.data.get("error")
                self.__log.debug("_ret_err=%s", _ret_err)
                if _ret_err is None:
                    _msg = '_ret.data["error"] is None'
                    self.__log.warning(_msg)
                    _result_list.append(_msg)
                    continue

                _ret_err_msg = _ret_err.get("message")
                self.__log.debug("_ret_err_msg=%a", _ret_err_msg)

                if _ret_err_msg != "Method not found":
                    _msg = f"error: {_ret_err_msg}"
                    self.__log.warning(_msg)
                    _result_list.append(_msg)

                continue

            #
            # キューイングすべきコマンドの処理
            #
            _result_list.append("queue")

            # method の prefix を変更して、
            # JSON-RPCリクエスト形式に整える
            _cmd_jsonstr = self.mk_jsonrpc_req(
                json.dumps(_cmd_dict),
                self.obj_exec.__class__.__name__.lower(),
            )
            self.__log.debug("_cmd_jsonstr=%a", _cmd_jsonstr)

            # キューイングすべきコマンドをリストに追加する。
            # キューイングは、あとでまとめて行う。
            _exec_cmd_jsondata_list.append(json.loads(_cmd_jsonstr))

        if _exec_cmd_jsondata_list:
            self.__log.debug(
                "_exec_cmd_jsondata_list=%a,qsize=%s",
                json.dumps(_exec_cmd_jsondata_list),
                self.qsize,
            )
            self.cmdq.put(_exec_cmd_jsondata_list)

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

            _cmd_data_list = self.recv()
            if not _cmd_data_list:
                continue
            self.__log.debug(
                "_cmd_data_list=%a, qsize=%s", _cmd_data_list, self.qsize
            )

            self._flag_busy = True

            for _cmd_data in _cmd_data_list:
                self.__log.debug("_cmd_data=%s", _cmd_data)

                try:
                    _cmd_str = json.dumps(_cmd_data)
                    ret = JSONRPCResponseManager.handle(
                        _cmd_str, self.dispatcher_exec
                    )
                    if ret:
                        self.__log.debug("ret.data=%s", ret.data)

                        if ret.data.get("error"):
                            self.__log.warning(
                                "_cmd_str=%s, ret.data=%s", _cmd_str, ret.data
                            )

                        if self.interval_sec > 0.0:
                            time.sleep(self.interval_sec)

                except Exception as e:
                    self.__log.error(errmsg(e))

        self.__log.debug("done.")

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


class HandleNotqueued:
    """Functions for notqueued."""

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
        while not self.worker.reqlist_q.empty():
            _cancel_count += 1
            _cmd = self.worker.reqlist_q.get()
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


class HandleQueue:
    """Functions for queue."""

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
        return True

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

    def move_pulse_relative(self, servo_i: int, pulse_diff: int):
        """Move one servo by relative pulse."""
        self.__log.debug("servo_i=%s,pulse_diff=%s", servo_i, pulse_diff)
        self.mservo.move_pulse_relative(servo_i, pulse_diff, forced=True)

    def set(self, servo_i: int, target: str, pulse: int = None) -> bool:
        """Set calibrated pulse as target."""
        self.__log.debug(
            "servo_i=%s,target=%s,pulse=%s", servo_i, target, pulse
        )

        if servo_i >= len(self.mservo.pins):
            self.__log.error(
                "Invalid servo_i=%s >= %s", servo_i, len(self.mservo.pins)
            )
            return False

        _target = target.lower()

        if _target == "center":
            self.mservo.set_pulse_center(servo_i, pulse)
            return True
        if _target == "min":
            self.mservo.set_pulse_min(servo_i, pulse)
            return True
        if _target == "max":
            self.mservo.set_pulse_max(servo_i, pulse)
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
        flag_verbose=False,
        debug=False,
    ) -> None:
        """Constructor."""
        super().__init__(daemon=True)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug(
            "pins=%s,first_move=%s,conf_file=%s,flag_verbose=%s",
            pins,
            first_move,
            conf_file,
            flag_verbose,
        )

        self.flag_verbose = flag_verbose

        self.mservo = MultiServo(
            pi, pins, first_move, conf_file, debug=self.__debug
        )

        self.reqlist_q: queue.Queue = queue.Queue()

        # dispatcher for notqueued
        self.obj_notqueued = HandleNotqueued(self, debug=self.__debug)
        self.obj_notqueued_classname = (
            self.obj_notqueued.__class__.__name__.lower()
        )
        self.dispatcher_notqueued = Dispatcher()
        self.dispatcher_notqueued.add_object(self.obj_notqueued)

        # dispatcher for queue
        self.obj_queue = HandleQueue(self.mservo, debug=self.__debug)
        self.obj_queue_classname = self.obj_queue.__class__.__name__.lower()
        self.dispatcher_queue = Dispatcher()
        self.dispatcher_queue.add_object(self.obj_queue)
        self.queue_class_name = self.obj_queue.__class__.__name__.lower()

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
        self.clear_reqlist_q()
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
        return self.reqlist_q.qsize()

    @property
    def is_busy(self) -> bool:
        """Busy flag."""
        return self._flag_busy

    def __del__(self):
        """Delete."""
        self._active = False
        self.__log.debug("")

    def clear_reqlist_q(self):
        """Clear command queue."""
        _count = 0
        while not self.reqlist_q.empty():
            _count += 1
            _cmd = self.reqlist_q.get()
            self.__log.debug("%2d:%s", _count, _cmd)

        self.__log.debug("count=%s", _count)
        return _count

    def mk_jsonrpc_req(self, cmd_dict: dict, method_prefix: str = "") -> dict:
        """Make JSON-RPC request.

        Args:
            cmd_dict (dict): e.g. {"method": "aaa", "params": [bbb, ccc]},
            mothod_prefix (str): e.g. "ppp"

        Returns:
            jsonrpc_req_str (str):
                '{
                     "method": "ppp.aaa"
                     "params": [bbb, ccc],
                     "jsonrpc": "2.0",
                     "id": 1
                 }'
        """
        self.__log.debug(
            "cmd_dict=%s, method_prefix=%a", cmd_dict, method_prefix
        )

        if not cmd_dict or not cmd_dict.get("method"):
            return {}

        _jsonrpc_req_dict = {
            "jsonrpc": "2.0",
            "method": "",
            "params": [],
            "id": 0,
        }

        try:
            # "id"
            _req_id = cmd_dict.get("id")
            if _req_id:
                self.rpc_id = _req_id
            else:
                self.rpc_id += 1
            _jsonrpc_req_dict["id"] = self.rpc_id

            # "method"
            _method_name = cmd_dict.get("method")
            if method_prefix:
                _method_name = f"{method_prefix}.{_method_name}"
            _jsonrpc_req_dict["method"] = _method_name

            # "params"
            _req_params = cmd_dict.get("params")
            if _req_params:
                _jsonrpc_req_dict["params"] = _req_params

            # return
            self.__log.debug("_jsonrpc_req_dict=%s", _jsonrpc_req_dict)
            return _jsonrpc_req_dict

        except Exception as e:
            self.__log.error(errmsg(e))
            return {}

    def call(self, cmd_dict_list: list[dict]) -> list:
        """Call(JSON-RPC).

        Args:
            cmd_dict_list (list[dict]):

        Returns:
            _reslut_list (list)
        """
        self.__log.debug("cmd_dict_list=%s", cmd_dict_list)

        _queue_jsonrpc_req_list = []  # キューイングすべきコマンドのリスト
        _result_list = []  # 結果リスト

        for _cmd_dict in cmd_dict_list:
            self.__log.debug("_cmd_dict=%s", _cmd_dict)

            if _cmd_dict["method"] == "ERROR":
                self.__log.error("Ignore: %s", _cmd_dict)
                _result_list.append(_cmd_dict)
                continue

            _method_name = (
                f"{self.obj_notqueued_classname}.{_cmd_dict['method']}"
            )
            if _method_name in list(self.dispatcher_notqueued):
                #
                # キューに入れない処理
                #

                # JSON-RPCリクエスト形式に整える
                _jsonrpc_req_dict = self.mk_jsonrpc_req(
                    _cmd_dict, self.obj_notqueued_classname
                )
                self.__log.debug("_jsonrpc_req_dict=%s", _jsonrpc_req_dict)

                # 実行
                _ret = JSONRPCResponseManager.handle(
                    json.dumps(_jsonrpc_req_dict), self.dispatcher_notqueued
                )

                if _ret and _ret.data:
                    _result_list.append(_ret.data)
                else:
                    _result_list.append({})

                continue

            _method_name = f"{self.obj_queue_classname}.{_cmd_dict['method']}"
            if _method_name in list(self.dispatcher_queue):
                #
                # キューイングすべきコマンドの処理
                #
                _result_list.append({"result": "queued"})

                # method の prefix を変更して、
                # JSON-RPCリクエスト形式に整える
                _jsonrpc_req_dict = self.mk_jsonrpc_req(
                    _cmd_dict, self.obj_queue_classname
                )
                # self.__log.debug("_jsonrpc_req_dict=%s", _jsonrpc_req_dict)

                # キューイングすべきコマンドをリストに追加する。
                # キューイングは、あとでまとめて行う。
                _queue_jsonrpc_req_list.append(_jsonrpc_req_dict)
                continue

            #
            # invalid method
            #
            _result = {
                "error": {
                    "message": f"invalid method: '{_cmd_dict['method']}'"
                }
            }
            _result_list.append(_result)
            self.__log.error("%s", _result)

        if _queue_jsonrpc_req_list:
            #
            # キューイングすべきコマンドの処理
            #
            self.__log.debug(
                "_queue_jsonrpc_req_list=%s, qsize=%s",
                _queue_jsonrpc_req_list,
                self.qsize,
            )
            self.reqlist_q.put(_queue_jsonrpc_req_list)

        self.__log.debug("_result_list=%s", _result_list)
        return _result_list

    def run(self):
        """Run."""
        self.__log.debug("")

        self._flag_active = True

        # メインループ
        while self._flag_active:
            if self.qsize == 0:
                self._flag_busy = False

            # キューからコマンド(リスト)を取り出す
            try:
                _req_dict_list = self.reqlist_q.get(
                    timeout=self.DEF_RECV_TIMEOUT
                )
            except queue.Empty:
                continue

            if not _req_dict_list:
                continue

            self.__log.info("qsize=%s", self.qsize)

            self._flag_busy = True

            # コマンドリストの中のコマンドを順番に実行
            for _req_dict in _req_dict_list:
                self.__log.info(
                    "req> %s%s",
                    _req_dict.get("method"),
                    _req_dict.get("params"),
                )

                ret = None
                try:
                    # ディスパッチ
                    ret = JSONRPCResponseManager.handle(
                        json.dumps(_req_dict), self.dispatcher_queue
                    )
                except Exception as e:
                    self.__log.error(errmsg(e))

                if ret is None:
                    # ???
                    self.__log.warning("ret is %s", ret)
                    continue

                #
                # ret is not None
                #
                self.__log.info(
                    "ret>   result:%s, error:%s",
                    ret.data.get("result"),
                    ret.data.get("error"),
                )

                # インターバルが設定されている場合はsleep
                if self.interval_sec > 0.0:
                    time.sleep(self.interval_sec)

        self.__log.debug("done.")

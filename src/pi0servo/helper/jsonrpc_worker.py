import json
import time
import threading
import queue

from jsonrpc import JSONRPCResponseManager, Dispatcher

from ..core.calibrable_servo import CalibrableServo
from ..core.multi_servo import MultiServo
from ..utils.mylogger import get_logger, errmsg


class Handle:
    """Handle."""

    def __init__(self, mservo, debug=False) -> None:
        """Constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")
        
        self.mservo = mservo

    def move_all_angles_sync(self, angles: list[int], move_sec, step_n):
        """Move all angles sync."""
        self.__log.debug(
            "angles=%s,move_sec=%s,step_n=%s", angles, move_sec, step_n
        )

    def move_all_angles_sync_relative(
        self, angles: list[int], move_sec, step_n
    ):
        """Move all angles sync."""
        self.__log.debug(
            "angles=%s,move_sec=%s,step_n=%s", angles, move_sec, step_n
        )


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
        debug=False
    ) -> None:
        """Constructor."""
        super().__init__(daemon=True)
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("pins=%s", pins)

        self.mservo = MultiServo(
            pi, pins, first_move, conf_file, debug=self.__debug
        )

        self.obj_handle = Handle(self.mservo, debug=self.__debug)

        self.dispacher = Dispatcher()
        self.dispacher.add_object(self.obj_handle)
        
        self.move_sec = MultiServo.DEF_MOVE_SEC
        self.step_n = MultiServo.DEF_STEP_N        
        self.interval_sec = self.DEF_INTERVAL_SEC

        self._cmdq = queue.Queue()
        self._flag_active = False
        self._flag_busy = False

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
        return self._cmdq.qsize()

    def __del__(self):
        """Delete."""
        self._active = False
        self.__log.debug("")

    def clear_cmdq(self):
        """Clear command queue."""
        _count = 0
        while not self._cmdq.empty():
            _count += 1
            _cmd = self._cmdq.get()
            self.__log.debug("%2d:%s", _count, _cmd)

        self.__log.debug("count=%s", _count)
        return _count

    def send(self, cmd_data: str | dict) -> dict:
        """Send cmd_data(JSON)"""
        self.__log.debug("cmd_data=%s", cmd_data)
        try:
            if isinstance(cmd_data, str):
                cmd_json = json.loads(cmd_data)
            else:
                cmd_json = cmd_data

            # コマンド名チェック
            cmd_name = cmd_json.get("method")

            # コマンドごとの処理
            # キューに入れない特別な処理を先に行う
            if cmd_name == self.CMD_CANCEL:  # キャンセル
                _count = self.clear_cmdq()
                _ret = self.mk_reply_result(_count, cmd_data)
                self.__log.debug("%s: _ret=%s", cmd_name, _ret)
                return _ret

            if cmd_name == self.CMD_QSIZE:  # キューサイズ
                _ret = self.mk_reply_result(self.qsize, cmd_data)
                self.__log.debug("%s: _ret=%s", cmd_name, _ret)
                return _ret

            if cmd_name == self.CMD_WAIT:  # Wait
                # すべてのコマンドが終了するまで待つ
                while self._busy_flag or self.qsize > 0:
                    self.__log.debug("waiting..")
                    time.sleep(0.3)
                _ret = self.mk_reply_result(self.qsize, cmd_data)
                self.__log.debug("%s: _ret=%s", cmd_name, _ret)
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

            self.__log.debug("qsize=%s", self.qsize)

            ret = None
            try:
                ret = JSONRPCResponseManager.handle(_cmd_data, self.dispacher)
            except Exception as e:
                self.__log.error(errmsg(e))

            if ret:
                self.__log.debug("ret.data=%s", ret.data)
                
        self.__log.debug("done.")

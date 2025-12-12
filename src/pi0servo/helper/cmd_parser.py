#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_to_json.py."""

import json
from typing import Any

from ..utils.mylogger import errmsg, get_logger


class CmdParser:
    """String Command to JSON."""

    ANGLE_MIN = -90
    ANGLE_CENTER = 0
    ANGLE_MAX = 90

    # コマンド文字列とJSONコマンド名のマッピング
    COMMAND_MAP: dict[str, str] = {
        # move command
        "mv": "move_all_angles_sync",
        "mr": "move_all_angles_sync_relative",
        # move paramters
        "sl": "sleep",
        "ms": "move_sec",
        "st": "step_n",
        "is": "interval",
        # for calibration
        "mp": "move_pulse_relative",
        "sc": "set",  # set center
        "sn": "set",  # set min
        "sx": "set",  # set max
        # cancel
        "ca": "cancel",
        "zz": "cancel",
        # qsize
        "qs": "qsize",
        "qq": "qsize",
        # wait
        "wa": "wait",
        "ww": "wait",
    }

    # 'mv'コマンドの角度パラメータのエイリアスマッピング
    ANGLE_ALIAS_MAP: dict[str, str] = {
        "x": "max",
        "n": "min",
        "c": "center",
    }

    # setコマンドのコマンド名と`target`の対応
    SET_TARGET: dict[str, str] = {
        "sc": "center",
        "sn": "min",
        "sx": "max",
    }

    def __init__(self, debug=False):
        """constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

    def _mk_err_data(
        self, method_name: str, err_name: str, err_data: str
    ) -> dict:
        """Make error data."""
        return {
            "result": "ERROR",
            "method": method_name,
            "error": err_name,
            "data": err_data,
        }

    def _mk_err_params(self, params: str, err_str: str) -> dict:
        """Make error params."""
        return {"result": "ERROR", "params": params, "error": err_str}

    def _parse_angles(self, angle_str: str) -> list[int | str | None] | None:
        """Parse angle parameters.
        'mv'コマンドのパラメータ文字列をパースして角度のリストを返す.

        e.g.
            "40,30,20,10"   --> [40,30,20,10]
            "-40,.,,,"       --> [-40,null,null,null]
            "mx,min,center" --> ["max","min","center"]
            "x,n,c"         --> ["max","min","center"]
            "x,.,center,20" --> ["max",null,"center",20]
        """
        self.__log.debug("angle_str=%a", angle_str)
        if not angle_str:
            return None

        angle_parts = angle_str.split(",")
        # self.__log.debug("angle_parts=%s", angle_parts)

        angles: list[int | str | None] = []

        for angle_part in angle_parts:
            _p = angle_part.strip().lower()

            if not _p:  # None: 動かさない
                angles.append(None)
                continue

            if _p == ".":  # None: 動かさない
                angles.append(None)
                continue

            if _p in self.ANGLE_ALIAS_MAP:
                angles.append(self.ANGLE_ALIAS_MAP[_p])
                continue

            if _p in ["max", "min", "center"]:
                angles.append(_p)
                continue

            # 数値
            try:
                angle = int(_p)
            except ValueError as e:
                self.__log.error(errmsg(e))
                # エラーの場合は None ではなく、エラーを示すオブジェクトを返す
                return None  # ここは None のままにする

            angles.append(angle)

        # self.__log.debug("angles=%s", angles)
        return angles

    def _parse_params_angles(self, cmd_params: str) -> dict:
        """Parse params: angles."""
        self.__log.debug("cmd_params=%a", cmd_params)

        if not cmd_params:
            return self._mk_err_params(cmd_params, "no params")

        angles = self._parse_angles(cmd_params)
        if angles is None:
            return self._mk_err_params(cmd_params, "invalid angles")

        return {"angles": angles}

    def _parse_params_angle_diffs(self, cmd_params: str) -> dict:
        """Parse parmas: angle_diffs."""
        self.__log.debug("cmd_params=%a", cmd_params)

        if not cmd_params:
            return self._mk_err_params(cmd_params, "no params")

        try:
            angle_diffs = [int(a) for a in cmd_params.split(",")]
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        if angle_diffs is None:
            return self._mk_err_params(cmd_params, "invalid angle_diffs")

        return {"angle_diffs": angle_diffs}

    def _parse_params_pulse_diffs(self, cmd_params: str) -> dict:
        """Parse parmas: pulse_diff."""
        self.__log.debug("cmd_params=%a", cmd_params)

        if not cmd_params:
            return self._mk_err_params(cmd_params, "no params")

        try:
            servo_i_str, pulse_diff_str = cmd_params.split(",", 1)
            servo_i = int(servo_i_str)
            pulse_diff = int(pulse_diff_str)
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        return {"servo_i": servo_i, "pulse_diff": pulse_diff}

    def _parse_params_sec(self, cmd_params: str) -> dict:
        """Parse params second."""
        self.__log.debug("cmd_params=%a", cmd_params)

        if not cmd_params:
            return self._mk_err_params(cmd_params, "no params")

        try:
            sec = float(cmd_params)
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        if sec < 0:
            return self._mk_err_params(cmd_params, "< 0")

        return {"sec": sec}

    def _parse_params_step_n(self, cmd_params: str) -> dict:
        """Parse params: step_n(int)."""
        self.__log.debug("cmd_params=%a", cmd_params)

        try:
            step_n = int(cmd_params)
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        if step_n < 1:
            return self._mk_err_params(cmd_params, "< 1")

        return {"step_n": step_n}

    def _parse_params_move_pulse(self, cmd_params: str) -> dict:
        """Parse params: move palse (idx, pulse)"""
        self.__log.debug("cmd_params=%a", cmd_params)

        try:
            servo_i_str, pulse_diff_str = cmd_params.split(",", 1)
            servo_i = int(servo_i_str)
            pulse_diff = int(pulse_diff_str)
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        return {"servo_i": servo_i, "pulse_dif": pulse_diff}

    def _parse_params_set(self, cmd_params: str) -> dict:
        """Parse params: ``set``method (servo_i, target, pulse)."""
        self.__log.debug("cmd_params=%a", cmd_params)

        params = cmd_params.split(",")
        if len(params) > 2:
            return self._mk_err_params(cmd_params, cmd_params)

        try:
            servo_i = int(params[0])
            pulse = None
            if len(params) == 2:
                pulse = int(params[1])
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        return {"servo_i": servo_i, "pulse": pulse}

    def cmdstr_to_json(self, cmd_str: str) -> dict:
        """Command string to command data(dict).

        Args:
            cmd_str (str): "mv:40,30", "sl:0.5" のようなコマンド文字列。

        Returns: (dict)
            変換されたコマンドデータ(dict)。
            変換できない場合はエラー情報を返す。
        """
        self.__log.debug("cmd_str=%s", cmd_str)

        if not isinstance(cmd_str, str):
            return self._mk_err_data(
                "???", "INVALID_CMD_FORMAT", str(cmd_str)
            )

        # e.g. "mv:10,20,30,40" --> ["mv", "10,20,30,40"]
        cmd_parts = cmd_str.split(":", 1)

        cmd_name = cmd_parts[0].lower()
        if len(cmd_parts) > 1:
            cmd_params = cmd_parts[1]
        else:
            cmd_params = ""

        if cmd_name not in self.COMMAND_MAP:
            _err_data = self._mk_err_data("???", "METHOD_NOT_FOUND", cmd_str)
            self.__log.error("%s", _err_data)
            return _err_data

        # e.g. "mv" --> "move_all_angles_sync"
        method_name = self.COMMAND_MAP[cmd_name]

        # cmd_dataの初期化
        cmd_data: dict[str, Any] = {"method": method_name}

        # コマンド別の処理
        if cmd_name == "mv":
            ret = self._parse_params_angles(cmd_params)
            if ret.get("result") == "ERROR":
                return ret
            cmd_data["params"] = ret

        elif cmd_name == "mr":
            ret = self._parse_params_angle_diffs(cmd_params)
            if ret.get("result") == "ERROR":
                return ret
            cmd_data["params"] = ret

        elif cmd_name == "mp":
            ret = self._parse_params_pulse_diffs(cmd_params)
            if ret.get("result") == "ERROR":
                return ret
            cmd_data["params"] = ret

        elif cmd_name in ["sl", "ms", "is"]:
            ret = self._parse_params_sec(cmd_params)
            if ret.get("result") == "ERROR":
                return ret
            cmd_data["params"] = ret

        elif cmd_name == "st":
            ret = self._parse_params_step_n(cmd_params)
            if ret.get("result") == "ERROR":
                return ret
            cmd_data["params"] = ret

        elif cmd_name in ("sc", "sn", "sx"):
            """
            "sc:1,1500"
            {
              "method": "set",
              "params": {
                "servo_i": 1,
                "target": "center"
                "pulse": 1500
              }
            }
            """
            # {"servo_i": servo_i, "pulse": pulse}
            ret = self._parse_params_set(cmd_params)
            if ret.get("result") == "ERROR":
                return ret

            cmd_data["params"] = {
                "servo_i": ret["servo_i"],
                "target": self.SET_TARGET[cmd_name],
                "pulse": ret["pulse"],
            }

        elif cmd_name in ["ca", "zz", "qs", "qq", "wa", "ww"]:
            pass

        else:
            _err_data = self._mk_err_data("???", "INVALID_CMD", cmd_str)
            self.__log.error("%s", _err_data)
            return _err_data

        self.__log.debug("cmd_data=%s", cmd_data)
        return cmd_data

    def cmdstr_to_jsonlist(self, cmd_line: str) -> list[dict]:
        """Command line to command string list."""

        cmd_data_list = []

        for cmd_str in cmd_line.strip().split():
            cmd_data = self.cmdstr_to_json(cmd_str)

            cmd_data_list.append(cmd_data)

            # if cmd_data.get("err"):
            #     break

        return cmd_data_list

    def cmdstr_to_jsonliststr(self, cmd_line: str) -> str:
        """Dict形式をJSON文字列に変換."""
        # self.__log.debug("cmd_line=%s", cmd_line)

        _json_data: list[dict] | dict = self.cmdstr_to_jsonlist(cmd_line)

        self.__log.debug('_json_data="%s"', _json_data)
        return json.dumps(_json_data)

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

    # 'mv'コマンドの角度パラメータのエイリアスマッピング
    ANGLE_ALIAS_MAP: dict[str, str] = {
        "x": "max",
        "n": "min",
        "c": "center",
    }

    def __init__(self, debug=False):
        """constractor."""
        self.__debug = debug
        self.__log = get_logger(self.__class__.__name__, self.__debug)
        self.__log.debug("")

        # コマンド文字列とメソッド名、パラメータのパーサーのマッピング
        self._cmd_map = {
            "mv": {
                "method": "move_all_angles_sync",
                "params": self._parse_params_angles,
                "info": "mv:30,-20  mv:c,n,x  mv:.,=,c,30",
            },
            "mr": {
                "method": "move_all_angles_sync_relative",
                "params": self._parse_params_angle_diffs,
                "info": "mr:10,-20",
            },
            # move paramters
            "sl": {
                "method": "sleep",
                "params": self._parse_params_sec,
                "info": "sl:1  sl:.5",
            },
            "ms": {
                "method": "move_sec",
                "params": self._parse_params_sec,
                "info": "ms:1  ms:.5",
            },
            "st": {
                "method": "step_n",
                "params": self._parse_params_step_n,
                "info": "st:50  st:2",
            },
            "is": {
                "method": "interval",
                "params": self._parse_params_sec,
                "info": "is:1  is:.5",
            },
            # for calibration
            "mp": {
                "method": "move_pulse_relative",
                "params": self._parse_params_move_pulse,
                "info": "mp:0,100  mp:1,-200",
            },
            "cb": {
                "method": "set",
                "params": self._parse_params_cb,
                "info": "cb:0,c  cb:1,n,500  cb2,x,2500",
            },
            # cancel
            "ca": {"method": "cancel", "params": None, "info": ""},
            "zz": {"method": "cancel", "params": None, "info": ""},
            # qsize
            "qs": {"method": "qsize", "params": None, "info": ""},
            "qq": {"method": "qsize", "params": None, "info": ""},
            # wait
            "wa": {"method": "wait", "params": None, "info": ""},
            "ww": {"method": "wait", "params": None, "info": ""},
        }

    @property
    def cmd_map(self):
        return self._cmd_map

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

        angles: list[int | str | None] = []

        for angle_part in angle_parts:
            _p = angle_part.strip().lower()

            if not _p:  # None: 動かさない
                angles.append(None)
                continue

            if _p in [".", "="]:  # None: 動かさない
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

        return {"servo_i": servo_i, "pulse_diff": pulse_diff}

    def _parse_params_cb(self, cmd_params: str) -> dict:
        """Parse params: ``cb->set``method (servo_i, target, pulse)."""
        self.__log.debug("cmd_params=%a", cmd_params)

        params = cmd_params.split(",")
        if len(params) > 3:
            return self._mk_err_params(cmd_params, cmd_params)

        try:
            servo_i = int(params[0])
            target = self.ANGLE_ALIAS_MAP[params[1]]
            pulse = None
            if len(params) == 3:
                pulse = int(params[2])
        except Exception as e:
            msg = errmsg(e)
            self.__log.warning(msg)
            return self._mk_err_params(cmd_params, msg)

        return {"servo_i": servo_i, "target": target, "pulse": pulse}

    def cmdstr_to_json(self, cmd_str: str) -> dict:
        # XXX TBD: mccabe: Cyclomatic complexity too high: 17 (threshold 15)
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

        if cmd_name not in self.cmd_map:
            _err_data = self._mk_err_data("???", "METHOD_NOT_FOUND", cmd_str)
            self.__log.error("%s", _err_data)
            return _err_data

        # e.g. "mv" --> "move_all_angles_sync"
        method_name = self.cmd_map[cmd_name]["method"]
        params_parser = self.cmd_map[cmd_name]["params"]

        # cmd_dataの初期化
        cmd_data: dict[str, Any] = {"method": method_name}

        # パラメータのパーズ
        if params_parser:
            ret = params_parser(cmd_params)
            if ret.get("result") == "ERROR":
                return ret

            cmd_data["params"] = ret

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

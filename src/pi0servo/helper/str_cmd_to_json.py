#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_to_json.py."""

import json
from typing import Any

from ..utils.mylogger import get_logger


class StrCmdToJson:
    """String Command to JSON."""

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

    # setコマンドのコマンドメイト`target`の対応
    SET_TARGET: dict[str, str] = {
        "sc": "center",
        "sn": "min",
        "sx": "max",
    }

    def __init__(self, angle_factor: list | None = None, debug=False):
        """constractor."""
        if angle_factor is None:
            angle_factor = []
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("angle_factor=%s", angle_factor)

        self._angle_factor = angle_factor  # property

    @property
    def angle_factor(self):
        """Get angle_factor."""
        return self._angle_factor

    @angle_factor.setter
    def angle_factor(self, af: list | None = None):
        """Set angle_factor."""
        if af is None:
            af = []
        self._angle_factor = af

    def _create_error_data(self, code_key: str, strcmd: str) -> dict:
        """Create error data."""
        return {"method": "ERROR", "error": code_key, "data": strcmd}

    def _parse_angles(self, angle_str: str) -> list[int | str | None] | None:
        """Parse angle parameters.
        'mv'コマンドのパラメータ文字列をパースして角度のリストを返す.

        e.g.
            "40,30,20,10"   --> [40,30,20,10]
            "-40,.,."       --> [-40,null,null]
            "mx,min,center" --> ["max","min","center"]
            "x,n,c"         --> ["max","min","center"]
            "x,.,center,20" --> ["max",null,"center",20]
        """
        angle_parts = angle_str.split(",")
        # self.__log.debug("angle_parts=%s", angle_parts)

        angles: list[int | str | None] = []

        for angle_part in angle_parts:
            _p = angle_part.strip().lower()
            # self.__log.debug("_p=%s", _p)
            if not _p:  # 空の要素は不正
                return None

            if _p == ".":  # None: 動かさない
                angles.append(None)

            elif _p in self.ANGLE_ALIAS_MAP:
                angles.append(self.ANGLE_ALIAS_MAP[_p])

            elif _p in ["max", "min", "center"]:
                angles.append(_p)

            else:  # 数値
                try:
                    angle = int(_p)
                    if not -90 <= angle <= 90:
                        return None  # 角度範囲外
                    angles.append(angle)
                except ValueError:
                    return None  # 数値に変換できない

        # self.__log.debug("angles=%s", angles)

        # angle_factor に応じて符号反転
        for _i in range(len(angles)):
            if _i >= len(self.angle_factor):
                break

            if isinstance(angles[_i], int):
                angles[_i] *= self.angle_factor[_i]

            elif self.angle_factor[_i] == -1:
                if angles[_i] == "min":
                    angles[_i] = "max"
                elif angles[_i] == "max":
                    angles[_i] = "min"

        self.__log.debug("angles=%s", angles)
        return angles

    def cmdstr_to_json(self, cmd_str: str) -> dict:
        """Command string to command data(dict).

        Args:
            cmd_str: "mv:40,30", "sl:0.5" のようなコマンド文字列。

        Returns: (dict)
            変換されたコマンドデータ(dict)。
            変換できない場合はエラー情報を返す。
        """
        self.__log.debug("cmd_str=%s", cmd_str)

        # 不正な文字列はエラー
        if not isinstance(cmd_str, str) or " " in cmd_str:
            return self._create_error_data("INVALID_REQUEST", cmd_str)

        # e.g. "mv:10,20,30,40" --> cmd_parts = ["mv", "10,20,30,40"]
        cmd_parts = cmd_str.split(":", 1)

        # e.g. cmd_key = "mv"
        cmd_key = cmd_parts[0].lower()

        if cmd_key not in self.COMMAND_MAP:
            return self._create_error_data("METHOD_NOT_FOUND", cmd_str)

        # コマンド名の取得 e.g. "mv" --> "move_all_angles_sync"
        cmd_name = self.COMMAND_MAP[cmd_key]

        # パラメータの取得
        if len(cmd_parts) == 1:
            cmd_param_str = ""
        else:
            cmd_param_str = cmd_parts[1]
        self.__log.debug(
            "cmd_key=%s, cmd_name=%s, cmd_param_str=%s",
            cmd_key,
            cmd_name,
            cmd_param_str,
        )

        # _cmd_dataの初期化
        _cmd_data: dict[str, Any] = {"method": cmd_name}

        # コマンド別の処理
        try:
            if cmd_key == "mv":
                if not cmd_param_str:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                angles = self._parse_angles(cmd_param_str)
                self.__log.debug("angles=%s", angles)
                if angles is None:
                    return self._create_error_data(
                        "INVALID_PARAM", cmd_param_str
                    )

                _cmd_data["params"] = {"angles": angles}

            elif cmd_key == "mr":
                if not cmd_param_str:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                angle_diffs = [
                    int(a) * self.angle_factor[i]
                    for i, a in enumerate(cmd_param_str.split(","))
                ]

                if angle_diffs is None:
                    return self._create_error_data(
                        "INVALID_PARAM", cmd_param_str
                    )

                _cmd_data["params"] = {"angle_diffs": angle_diffs}

            elif cmd_key in ["sl", "ms", "is"]:
                sec = float(cmd_param_str)
                if sec < 0:
                    return self._create_error_data("INVALID_PARAM", cmd_str)
                _cmd_data["params"] = {"sec": sec}

            elif cmd_key == "st":
                _n = int(cmd_param_str)
                if _n < 1:
                    return self._create_error_data("INVALID_PARAM", cmd_str)
                _cmd_data["params"] = {"n": _n}

            elif cmd_key == "mp":
                if not cmd_param_str:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                sv_idx_str, p_diff_str = cmd_param_str.split(",")
                sv_idx = int(sv_idx_str)
                p_diff = int(p_diff_str) * self.angle_factor[sv_idx]

                _cmd_data["params"] = {
                    "servo_idx": sv_idx,
                    "pulse_diff": p_diff,
                }

            elif cmd_key in ("sc", "sn", "sx"):
                servo = int(cmd_param_str)
                target = self.SET_TARGET[cmd_key]
                if self.angle_factor[servo] < 0:
                    if target == "min":
                        target = "max"
                    elif target == "max":
                        target = "min"
                self.__log.debug("servo=%s, target=%s", servo, target)
                _cmd_data["params"] = {"servo_i": servo, "target": target}

            elif cmd_key in ["ca", "zz", "qs", "qq", "wa", "ww"]:
                pass

        except (ValueError, TypeError, IndexError) as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return self._create_error_data("INVALID_PARAM", cmd_str)

        self.__log.debug("_cmd_data=%s", _cmd_data)
        return _cmd_data

    def cmdstr_to_jsonlist(self, cmd_line: str) -> list[dict]:
        """Command line to command string list."""

        _cmd_data_list = []

        for cmd_str in cmd_line.split():
            _cmd_data = self.cmdstr_to_json(cmd_str)
            # self.__log.debug("cmd_data=%s", _cmd_data)

            _cmd_data_list.append(_cmd_data)

            if _cmd_data.get("err"):
                break

        return _cmd_data_list

    def cmdstr_to_jsonliststr(self, cmd_line: str) -> str:
        """Dict形式をJSON文字列に変換."""
        # self.__log.debug("cmd_line=%s", cmd_line)

        _json_data: list[dict] | dict = self.cmdstr_to_jsonlist(cmd_line)

        self.__log.debug('_json_data="%s"', _json_data)
        return json.dumps(_json_data)

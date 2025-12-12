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

    def _create_error_data(self, code_key: str, strcmd: str) -> dict:
        """Create error data."""
        return {"method": "ERROR", "error": code_key, "data": strcmd}

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

    def _parse_params_mv(self, cmd_params) -> dict:
        """Parse command 'mv'."""
        pass

    def cmdstr_to_json(self, cmd_str: str) -> dict:
        """Command string to command data(dict).

        Args:
            cmd_str (str): "mv:40,30", "sl:0.5" のようなコマンド文字列。

        Returns: (dict)
            変換されたコマンドデータ(dict)。
            変換できない場合はエラー情報を返す。
        """
        self.__log.debug("cmd_str=%s", cmd_str)

        # e.g. "mv:10,20,30,40" --> ["mv", "10,20,30,40"]
        cmd_parts = cmd_str.split(":", 1)

        cmd_name = cmd_parts[0].lower()
        if len(cmd_parts) > 1:
            cmd_params = cmd_parts[1]
        else:
            cmd_params = ""

        if cmd_name not in self.COMMAND_MAP:
            _err_dict = self._create_error_data("METHOD_NOT_FOUND", cmd_str)
            self.__log.error("%s", _err_dict)
            return _err_dict

        # e.g. "mv" --> "move_all_angles_sync"
        method_name = self.COMMAND_MAP[cmd_name]

        # _cmd_dataの初期化
        cmd_data: dict[str, Any] = {"method": method_name}

        # コマンド別の処理
        try:
            if cmd_name == "mv":
                if not cmd_params:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                angles = self._parse_angles(cmd_params)
                # self.__log.debug("angles=%s", angles)
                if angles is None:  # _parse_angles が None を返した場合
                    return self._create_error_data(
                        "INVALID_PARAM", cmd_params
                    )

                cmd_data["params"] = {"angles": angles}

            elif cmd_name == "mr":
                if not cmd_params:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                angle_diffs = [int(a) for a in cmd_params.split(",")]
                self.__log.debug("angle_diffs=%s", angle_diffs)

                if angle_diffs is None:
                    return self._create_error_data(
                        "INVALID_PARAM", cmd_params
                    )

                cmd_data["params"] = {"angle_diffs": angle_diffs}

            elif cmd_name in ["sl", "ms", "is"]:
                try:
                    sec = float(cmd_params)
                    if sec < 0:
                        return self._create_error_data(
                            "INVALID_PARAM", cmd_str
                        )
                    cmd_data["params"] = {"sec": sec}
                except Exception as e:
                    self.__log.warning(errmsg(e))
                    return self._create_error_data("INVALID_PARAM", cmd_str)

            elif cmd_name == "st":
                try:
                    _n = int(cmd_params)
                    if _n < 1:
                        return self._create_error_data(
                            "INVALID_PARAM", cmd_str
                        )
                    cmd_data["params"] = {"step_n": _n}
                except Exception as e:
                    self.__log.warning(errmsg(e))
                    return self._create_error_data("INVALID_PARAM", cmd_str)

            elif cmd_name == "mp":
                if not cmd_params:
                    return self._create_error_data("INVALID_PARAM", cmd_str)

                try:
                    sv_idx_str, p_diff_str = cmd_params.split(",")
                    sv_idx = int(sv_idx_str)
                    p_diff = int(p_diff_str)

                    cmd_data["params"] = {
                        "servo_i": sv_idx,
                        "pulse_diff": p_diff,
                    }
                except Exception as e:
                    self.__log.warning(errmsg(e))
                    return self._create_error_data("INVALID_PARAM", cmd_str)

            elif cmd_name in ("sc", "sn", "sx"):
                """
                XXX TBD: パスル指定できるよにすべき？

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
                try:
                    params = cmd_params.split(",", 1)

                    servo_i = int(params[0])

                    pulse: int | None = None
                    if len(params) > 1:
                        pulse = int(params[1])

                    target = self.SET_TARGET[cmd_name]

                    self.__log.debug(
                        "servo_i=%s,target=%s,pulse=%s",
                        servo_i,
                        target,
                        pulse,
                    )

                    cmd_data["params"] = {
                        "servo_i": servo_i,
                        "target": target,
                        "pulse": pulse,
                    }
                except Exception as e:
                    self.__log.warning(errmsg(e))
                    return self._create_error_data("INVALID_PARAM", cmd_str)

            elif cmd_name in ["ca", "zz", "qs", "qq", "wa", "ww"]:
                pass

        except (ValueError, TypeError, IndexError) as _e:
            self.__log.error("%s: %s", type(_e).__name__, _e)
            return self._create_error_data("INVALID_PARAM", cmd_str)

        self.__log.debug("cmd_data=%s", cmd_data)
        return cmd_data

    def cmdstr_to_jsonlist(self, cmd_line: str) -> list[dict]:
        """Command line to command string list."""

        cmd_data_list = []

        for cmd_str in cmd_line.strip().split():  # .strip() を追加
            cmd_data = self.cmdstr_to_json(cmd_str)
            # self.__log.debug("cmd_data=%s", cmd_data)

            cmd_data_list.append(cmd_data)

            if cmd_data.get("err"):
                break

        return cmd_data_list

    def cmdstr_to_jsonliststr(self, cmd_line: str) -> str:
        """Dict形式をJSON文字列に変換."""
        # self.__log.debug("cmd_line=%s", cmd_line)

        _json_data: list[dict] | dict = self.cmdstr_to_jsonlist(cmd_line)

        self.__log.debug('_json_data="%s"', _json_data)
        return json.dumps(_json_data)

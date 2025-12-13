#
# (c) 2025 Yoichi Tanibayashi
#
"""cmd_to_json.py."""

import json
import os
from typing import Any

from dynaconf import Dynaconf

from ..utils.mylogger import errmsg, get_logger


class CmdParser:
    """String Command to JSON."""

    CONF_PATH = [".", "~", "/etc"]  # 優先度順
    CONF_FILENAME = "cmds.toml"

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

        #
        # 設定ファイルの読み込み
        #
        # 設定ファイルの
        self.settings_files = []
        for p in self.CONF_PATH:
            file_path = os.path.expanduser(f"{p}/{self.CONF_FILENAME}")
            if os.path.exists(file_path):
                self.settings_files.append(file_path)
        self.__log.info(
            "settings_file: select %a from %s",
            self.settings_files[0],
            self.settings_files,
        )

        if self.settings_files:
            try:
                # 上書き読み込みせず、一つだけ読み込む
                self.conf = Dynaconf(settings_files=[self.settings_files[0]])
            except Exception as e:
                self.__log.error(errmsg(e))
                # raise e
        else:
            self.__log.error(
                "no settings file(%a) in %s",
                self.CONF_FILENAME,
                self.CONF_PATH,
            )
            raise FileExistsError

        self.__log.debug("conf=%s", self.conf)

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

    def _parse_params_calib(self, cmd_params: str) -> dict:
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

    def parse_to_json(self, cmd_str: str) -> dict:
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
        cmd_params = ""
        if len(cmd_parts) > 1:
            cmd_params = cmd_parts[1]

        if cmd_name not in self.conf:
            _err_data = self._mk_err_data("???", "METHOD_NOT_FOUND", cmd_str)
            self.__log.error("%s", _err_data)
            return _err_data

        # e.g. "mv" --> "move_all_angles_sync"
        method_name = self.conf[cmd_name]["method"]
        paramtype = self.conf[cmd_name]["paramtype"]

        # cmd_dataの初期化
        cmd_data: dict[str, Any] = {"method": method_name}

        # パラメータのパーズ
        if paramtype:
            params_parser = getattr(self, "_parse_params_" + paramtype)
            if params_parser:
                ret = params_parser(cmd_params)
                if ret.get("result") == "ERROR":
                    return ret
                cmd_data["params"] = ret

        self.__log.info("cmd_data=%s", cmd_data)
        return cmd_data

    def parse_to_jsonlist(self, cmd_line: str) -> list[dict]:
        """Command line to command string list."""

        cmd_data_list = []

        for cmd_str in cmd_line.strip().split():
            cmd_data = self.parse_to_json(cmd_str)

            cmd_data_list.append(cmd_data)

            # if cmd_data.get("err"):
            #     break

        return cmd_data_list

    def parse_to_jsonliststr(self, cmd_line: str) -> str:
        """Dict形式をJSON文字列に変換."""
        # self.__log.debug("cmd_line=%s", cmd_line)

        _json_data: list[dict] | dict = self.parse_to_jsonlist(cmd_line)

        self.__log.debug('_json_data="%s"', _json_data)
        return json.dumps(_json_data)

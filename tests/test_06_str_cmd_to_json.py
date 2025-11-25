#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_06_str_cmd_to_json.py
"""

import json

import pytest

from pi0servo.helper.str_cmd_to_json import StrCmdToJson


@pytest.fixture
def str_cmd_to_json_instance():
    """StrCmdToJsonのテスト用インスタンスを生成するフィクスチャ"""
    return StrCmdToJson(angle_factor=[1, 1, 1, 1], debug=True)


class TestStrCmdToJson:
    """StrCmdToJsonクラスのテスト"""

    def test_init(self, str_cmd_to_json_instance):
        """初期化のテスト"""
        assert str_cmd_to_json_instance._debug is True
        assert str_cmd_to_json_instance.angle_factor == [1, 1, 1, 1]

    def test_init_empty_angle_factor(self):
        """angle_factorが空のリストの場合の初期化テスト"""
        instance = StrCmdToJson(angle_factor=[], debug=False)
        assert instance._debug is False
        assert instance.angle_factor == []

    def test_init_debug_false(self):
        """debug=Falseの場合の初期化テスト"""
        instance = StrCmdToJson(debug=False)
        assert instance._debug is False

    def test_angle_factor_setter(self):
        """angle_factorセッターのテスト"""
        instance = StrCmdToJson()
        new_factor = [0, 0, 0, 0]
        instance.angle_factor = new_factor
        assert instance.angle_factor == new_factor

    def test_create_error_data(self):
        """_create_error_dataのテスト"""
        instance = StrCmdToJson()
        error_data = instance._create_error_data("INVALID_PARAM", "mv:abc")
        assert error_data == {
            "method": "ERROR",
            "error": "INVALID_PARAM",
            "data": "mv:abc",
        }

    def test_parse_angles_angle_factor_shorter(self):
        """_parse_anglesでangle_factorがanglesより短い場合のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1], debug=True)
        angle_str = "40,30,20"
        expected_angles = [
            40,
            -30,
            20,
        ]  # 3番目の角度にはangle_factorが適用されない
        result = instance._parse_angles(angle_str)
        assert result == expected_angles

    def test_parse_angles_angle_factor_longer(self):
        """_parse_anglesでangle_factorがanglesより長い場合のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1, 1, -1], debug=True)
        angle_str = "40,30"
        expected_angles = [40, -30]
        result = instance._parse_angles(angle_str)
        assert result == expected_angles

    def test_parse_angles_empty_part(self):
        """_parse_anglesで空の角度要素がある場合のテスト"""
        instance = StrCmdToJson()
        angle_str = "10,,20"
        expected_angles = [10, None, 20]

        result = instance._parse_angles(angle_str)
        assert result == expected_angles

    def test_cmdstr_to_json_invalid_str_with_space(self):
        """cmdstr_to_jsonでスペースを含む正な文字列のテスト"""
        instance = StrCmdToJson()
        cmd_str = "mv:10 20"
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_REQUEST",
            "data": "mv:10 20",
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    def test_cmdstr_to_json_not_string(self):
        """cmdstr_to_jsonで文字列ではない入力のテスト"""
        instance = StrCmdToJson()
        cmd_str = 123  # int型
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_REQUEST",
            "data": 123,
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    def test_cmdstr_to_json_mp_index_error(self):
        """cmdstr_to_jsonでmpコマンドのangle_factorインデックスエラーのテスト"""
        instance = StrCmdToJson(
            angle_factor=[1], debug=True
        )  # angle_factorが短い
        cmd_str = "mp:1,-50"  # servo_i=1 はangle_factorの範囲外
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_PARAM",
            "data": "mp:1,-50",
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    def test_cmdstr_to_json_set_index_error(self):
        """cmdstr_to_jsonでsetコマンドのangle_factorインデックスエラーのテスト"""
        instance = StrCmdToJson(
            angle_factor=[1], debug=True
        )  # angle_factorが短い
        cmd_str = "sn:1"  # servo_i=1 はangle_factorの範囲外
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_PARAM",
            "data": "sn:1",
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    def test_cmdstr_to_jsonlist_empty_line(self):
        """cmdstr_to_jsonlistで空のコマンドラインのテスト"""
        instance = StrCmdToJson()
        cmd_line = ""
        expected_json_obj = []
        result = instance.cmdstr_to_jsonlist(cmd_line)
        assert result == expected_json_obj

    def test_cmdstr_to_json_negative_sec(self):
        """cmdstr_to_jsonで負のsecパラメータのテスト"""
        instance = StrCmdToJson()
        cmd_str = "sl:-0.5"
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_PARAM",
            "data": "sl:-0.5",
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    def test_cmdstr_to_json_step_n_less_than_one(self):
        """cmdstr_to_jsonでstep_nが1未満のテスト"""
        instance = StrCmdToJson()
        cmd_str = "st:0"
        expected_json_obj = {
            "method": "ERROR",
            "error": "INVALID_PARAM",
            "data": "st:0",
        }
        result = instance.cmdstr_to_json(cmd_str)
        assert result == expected_json_obj

    @pytest.mark.parametrize(
        ("cmd_str", "expected_json_obj"),
        [
            (
                "mv:40,30,20,10",
                [
                    {
                        "method": "move_all_angles_sync",
                        "params": {"angles": [40, 30, 20, 10]},
                    }
                ],
            ),
            (
                "mv:x,n,c",
                [
                    {
                        "method": "move_all_angles_sync",
                        "params": {"angles": ["max", "min", "center"]},
                    }
                ],
            ),
            (
                "mr:10,20,-30,-40",
                [
                    {
                        "method": "move_all_angles_sync_relative",
                        "params": {"angle_diffs": [10, 20, -30, -40]},
                    }
                ],
            ),
            ("sl:0.5", [{"method": "sleep", "params": {"sec": 0.5}}]),
            (
                "mp:0,-50",
                [
                    {
                        "method": "move_pulse_relative",
                        "params": {"servo_i": 0, "pulse_diff": -50},
                    }
                ],
            ),
            (
                "sc:0",
                [
                    {
                        "method": "set",
                        "params": {"servo_i": 0, "target": "center"},
                    }
                ],
            ),
            ("ca", [{"method": "cancel"}]),
            ("zz", [{"method": "cancel"}]),
            ("wa", [{"method": "wait"}]),
            ("ww", [{"method": "wait"}]),
            (
                "mv:.",
                [
                    {
                        "method": "move_all_angles_sync",
                        "params": {"angles": [None]},
                    }
                ],
            ),
            (
                "mv:x,.,c,20",
                [
                    {
                        "method": "move_all_angles_sync",
                        "params": {"angles": ["max", None, "center", 20]},
                    }
                ],
            ),
            (
                "mv:100",
                [
                    {
                        "method": "move_all_angles_sync",
                        "params": {"angles": [90]},
                    }
                ],
            ),
            (
                "mv:abc",
                [
                    {
                        "method": "ERROR",
                        "error": "INVALID_PARAM",
                        "data": "abc",
                    }
                ],
            ),
            (
                "unknown:10",
                [
                    {
                        "method": "ERROR",
                        "error": "METHOD_NOT_FOUND",
                        "data": "unknown:10",
                    }
                ],
            ),
            (
                "sl:abc",
                [
                    {
                        "method": "ERROR",
                        "error": "INVALID_PARAM",
                        "data": "sl:abc",
                    }
                ],
            ),
            (
                "mv:",
                [
                    {
                        "method": "ERROR",
                        "error": "INVALID_PARAM",
                        "data": "mv:",
                    }
                ],
            ),
        ],
    )
    def test_cmdstr_to_jsonliststr(
        self, str_cmd_to_json_instance, cmd_str, expected_json_obj
    ):
        """cmdstr_to_jsonliststrのテスト"""
        result_json_str = str_cmd_to_json_instance.cmdstr_to_jsonliststr(
            cmd_str
        )
        result_obj = json.loads(result_json_str)
        assert result_obj == expected_json_obj

    def test_angle_factor_inversion(self):
        """angle_factorによる符号反転のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1, 1, -1], debug=True)
        cmd_str = "mv:40,30,20,10"
        expected_json_obj = [
            {
                "method": "move_all_angles_sync",
                "params": {"angles": [40, -30, 20, -10]},
            }
        ]
        result = instance.cmdstr_to_jsonliststr(cmd_str)
        result_obj = json.loads(result)
        assert result_obj == expected_json_obj

        cmd_str_alias = "mv:x,n,c,x"
        expected_json_obj_alias = [
            {
                "method": "move_all_angles_sync",
                "params": {"angles": ["max", "max", "center", "min"]},
            }
        ]
        result_alias = instance.cmdstr_to_jsonliststr(cmd_str_alias)
        result_obj_alias = json.loads(result_alias)
        assert result_obj_alias == expected_json_obj_alias

    def test_set_command_target_inversion(self):
        """setコマンドのtarget反転のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1, 1, 1], debug=True)

        # servo 0 (angle_factor=1) -> target: center
        cmd_str_sc0 = "sc:0"
        expected_json_obj_sc0 = [
            {"method": "set", "params": {"servo_i": 0, "target": "center"}}
        ]
        result_sc0 = instance.cmdstr_to_jsonliststr(cmd_str_sc0)
        result_obj_sc0 = json.loads(result_sc0)
        assert result_obj_sc0 == expected_json_obj_sc0

        # servo 1 (angle_factor=-1) -> target: min -> max
        cmd_str_sn1 = "sn:1"
        expected_json_obj_sn1 = [
            {"method": "set", "params": {"servo_i": 1, "target": "max"}}
        ]
        result_sn1 = instance.cmdstr_to_jsonliststr(cmd_str_sn1)
        result_obj_sn1 = json.loads(result_sn1)
        assert result_obj_sn1 == expected_json_obj_sn1

        # servo 1 (angle_factor=-1) -> target: max -> min
        cmd_str_sx1 = "sx:1"
        expected_json_obj_sx1 = [
            {"method": "set", "params": {"servo_i": 1, "target": "min"}}
        ]
        result_sx1 = instance.cmdstr_to_jsonliststr(cmd_str_sx1)
        result_obj_sx1 = json.loads(result_sx1)
        assert result_obj_sx1 == expected_json_obj_sx1

    def test_multiple_commands_in_line(self, str_cmd_to_json_instance):
        """複数コマンドが1行にある場合のテスト"""
        cmd_line = "mv:40,30 sl:0.1 mv:x,n"
        expected_json_obj = [
            {
                "method": "move_all_angles_sync",
                "params": {"angles": [40, 30]},
            },
            {"method": "sleep", "params": {"sec": 0.1}},
            {
                "method": "move_all_angles_sync",
                "params": {"angles": ["max", "min"]},
            },
        ]
        result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_line)
        result_obj = json.loads(result)
        assert result_obj == expected_json_obj

    def test_multiple_commands_with_error(self, str_cmd_to_json_instance):
        """複数コマンド中にエラーがある場合のテスト"""
        cmd_line = "mv:40,30 unknown:10 sl:0.1"
        expected_json_obj = [
            {
                "method": "move_all_angles_sync",
                "params": {"angles": [40, 30]},
            },
            {
                "method": "ERROR",
                "error": "METHOD_NOT_FOUND",
                "data": "unknown:10",
            },
            {"method": "sleep", "params": {"sec": 0.1}},
        ]
        result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_line)
        result_obj = json.loads(result)
        assert result_obj == expected_json_obj

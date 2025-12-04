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
    return StrCmdToJson(debug=True)


class TestStrCmdToJson:
    """StrCmdToJsonクラスのテスト"""

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
        instance = StrCmdToJson(debug=True)
        angle_str = "40,30,20"
        expected_angles = [
            40,
            30,
            20,
        ]  # 3番目の角度にはangle_factorが適用されない
        result = instance._parse_angles(angle_str)
        assert result == expected_angles

    def test_parse_angles_angle_factor_longer(self):
        """_parse_anglesでangle_factorがanglesより長い場合のテスト"""
        instance = StrCmdToJson(debug=True)
        angle_str = "40,30"
        expected_angles = [40, 30]

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
        print(result)
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

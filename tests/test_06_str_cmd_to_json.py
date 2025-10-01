#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_06_str_cmd_to_json.py
"""

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

    @pytest.mark.parametrize(
        "cmd_str, expected_json_str",
        [
            (
                "mv:40,30,20,10",
                (
                    '[{'
                    '"method": "move_all_angles_sync", '
                    '"params": {"angles": [40, 30, 20, 10]}'
                    '}]'
                ),
            ),
            (
                "mv:x,n,c",
                (
                    '[{'
                    '"method": "move_all_angles_sync", '
                    '"params": {"angles": ["max", "min", "center"]}'
                    '}]'
                ),
            ),
            ("sl:0.5", '[{"method": "sleep", "params": {"sec": 0.5}}]'),
            (
                "mp:100,-50",
                (
                    '[{'
                    '"method": "move_all_pulses_relative", '
                    '"params": {"pulse_diffs": [100, -50]}'
                    '}]'
                ),
            ),
            (
                "sc:0",
                (
                    '[{'
                    '"method": "set", '
                    '"params": {"servo": 0, "target": "center"}'
                    '}]'
                )
            ),
            ("ca", '[{"method": "cancel"}]'),
            ("zz", '[{"method": "cancel"}]'),
            ("wa", '[{"method": "wait"}]'),
            ("ww", '[{"method": "wait"}]'),
            (
                "mv:.",
                '[{'
                '"method": "move_all_angles_sync", '
                '"params": {"angles": [null]}'
                '}]'
            ),
            (
                "mv:x,.,c,20",
                (
                    '[{'
                    '"method": "move_all_angles_sync", '
                    '"params": {"angles": ["max", null, "center", 20]}'
                    '}]'
                ),
            ),
            ("mv:100", '[{"error": "INVALID_PARAM", "data": "mv:100"}]'),
            ("mv:abc", '[{"error": "INVALID_PARAM", "data": "mv:abc"}]'),
            (
                "unknown:10",
                '[{"error": "METHOD_NOT_FOUND", "data": "unknown:10"}]'
            ),
            ("sl:abc", '[{"error": "INVALID_PARAM", "data": "sl:abc"}]'),
            ("mv:", '[{"error": "INVALID_PARAM", "data": "mv:"}]'),
        ],
    )
    def test_cmdstr_to_jsonliststr(
        self, str_cmd_to_json_instance, cmd_str, expected_json_str
    ):
        """cmdstr_to_jsonliststrのテスト"""
        result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_str)
        assert result == expected_json_str

    def test_angle_factor_inversion(self):
        """angle_factorによる符号反転のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1, 1, -1], debug=True)
        cmd_str = "mv:40,30,20,10"
        expected_json_str = (
            '[{'
            '"method": "move_all_angles_sync", '
            '"params": {"angles": [40, -30, 20, -10]}'
            '}]'
        )
        result = instance.cmdstr_to_jsonliststr(cmd_str)
        assert result == expected_json_str

        cmd_str_alias = "mv:x,n,c,x"
        expected_json_str_alias = (
            (
                '['
                '{'
                '"method": "move_all_angles_sync", '
                '"params": {"angles": ["max", "max", "center", "min"]}'
                '}'
                ']'
            )
        )
        result_alias = instance.cmdstr_to_jsonliststr(cmd_str_alias)
        assert result_alias == expected_json_str_alias

    def test_set_command_target_inversion(self):
        """setコマンドのtarget反転のテスト"""
        instance = StrCmdToJson(angle_factor=[1, -1, 1, 1], debug=True)

        # servo 0 (angle_factor=1) -> target: center
        cmd_str_sc0 = "sc:0"
        expected_json_str_sc0 = (
            '[{'
            '"method": "set", '
            '"params": {"servo": 0, "target": "center"}'
            '}]'
        )
        result_sc0 = instance.cmdstr_to_jsonliststr(cmd_str_sc0)
        assert result_sc0 == expected_json_str_sc0

        # servo 1 (angle_factor=-1) -> target: min -> max
        cmd_str_sn1 = "sn:1"
        expected_json_str_sn1 = (
            '[{'
            '"method": "set", '
            '"params": {"servo": 1, "target": "max"}'
            '}]'
        )
        result_sn1 = instance.cmdstr_to_jsonliststr(cmd_str_sn1)
        assert result_sn1 == expected_json_str_sn1

        # servo 1 (angle_factor=-1) -> target: max -> min
        cmd_str_sx1 = "sx:1"
        expected_json_str_sx1 = (
            '[{'
            '"method": "set", '
            '"params": {"servo": 1, "target": "min"}'
            '}]'
        )
        result_sx1 = instance.cmdstr_to_jsonliststr(cmd_str_sx1)
        assert result_sx1 == expected_json_str_sx1

    def test_multiple_commands_in_line(self, str_cmd_to_json_instance):
        """複数コマンドが1行にある場合のテスト"""
        cmd_line = "mv:40,30 sl:0.1 mv:x,n"
        expected_json_str = (
            '['
            '{'
            '"method": "move_all_angles_sync", '
            '"params": {"angles": [40, 30]}'
            '}, '
            '{"method": "sleep", "params": {"sec": 0.1}}, '
            '{'
            '"method": "move_all_angles_sync", '
            '"params": {"angles": ["max", "min"]}'
            '}'
            ']'
        )
        result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_line)
        assert result == expected_json_str

    def test_multiple_commands_with_error(self, str_cmd_to_json_instance):
        """複数コマンド中にエラーがある場合のテスト"""
        cmd_line = "mv:40,30 unknown:10 sl:0.1"
        expected_json_str = (
            '['
            '{'
            '"method": "move_all_angles_sync", '
            '"params": {"angles": [40, 30]}'
            '}, '
            '{'
            '"error": "METHOD_NOT_FOUND", "data": "unknown:10"'
            '}, '
            '{"method": "sleep", "params": {"sec": 0.1}}'
            ']'
        )
        result = str_cmd_to_json_instance.cmdstr_to_jsonliststr(cmd_line)
        assert result == expected_json_str

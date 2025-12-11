#
# (c) 2025 Yoichi Tanibayashi
#
import pytest

from pi0servo.helper.commonlib import CommonLib

_CommonLib = CommonLib(debug=True)


# @pytest.fixture
# def commonlib():
#     return CommonLib(debug=True)


class TestCommonLib:
    """Test CommonLib class."""

    @pytest.mark.parametrize(
        ("pins_str", "pins"),
        [
            ("10", [10]),
            ("20-", [-20]),
            ("30,31,32,33", [30, 31, 32, 33]),
            ("30,-31,32-,-33", [30, -31, -32, -33]),
            ("a-, 31 ,32- , bbb", []),
            # 新しいテストケース
            ("", []),  # 空文字列
            (" ", []),  # スペースのみ
            (" 10 , 20 - , 30 ", [10, -20, 30]),  # 複数のスペース
            ("-", []),  # '-' のみの要素
            ("10,abc,20", []),  # 有効と無効の混合 (無効な部分で ValueError が発生し、空リストを返す)
            ("10,-20,def", []),  # 同上
            (" -10, 20- ", [-10, -20]), # 数値のみの負の値とスペース混在
        ],
    )
    def test_pins_str2list(self, pins_str, pins):
        clib = CommonLib(debug=True)
        res_pins = clib.pins_str2list(pins_str)

        assert res_pins == pins

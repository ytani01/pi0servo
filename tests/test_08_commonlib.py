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
        ],
    )
    def test_parse_pins_str(self, pins_str, pins):
        clib = CommonLib(debug=True)
        res_pins = clib.pins_str2list(pins_str)

        assert res_pins == pins

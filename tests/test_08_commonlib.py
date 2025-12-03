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
        ("pins_str", "pins", "angle_factors"),
        [
            ("10", [10], [1]),
            ("20-", [20], [-1]),
            ("30,31,32,33", [30, 31, 32, 33], [1, 1, 1, 1]),
            ("30-,31,32-,33", [30, 31, 32, 33], [-1, 1, -1, 1]),
            (" 30-, 31 ,32- , 33", [30, 31, 32, 33], [-1, 1, -1, 1]),
            ("a-, 31 ,32- , bbb", [], []),
        ],
    )
    def test_parse_pins_str(self, pins_str, pins, angle_factors):
        res_pins, res_angle_factors = _CommonLib.parse_pins_str(pins_str)

        assert res_pins == pins
        assert res_angle_factors == angle_factors

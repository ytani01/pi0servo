#
# (c) 2025 Yoichi Tanibayashi
#
import pytest

from pi0servo.helper.cmdlib import CmdLib

_CmdLib = CmdLib(debug=True)


# @pytest.fixture
# def cmdlib():
#     return CmdLib(debug=True)


class TestCmdLine:
    """Test CmdLine class."""

    @pytest.mark.parametrize(
        ("pins_str", "pins", "angle_factors"),
        [
            ("10", [10], [1]),
            ("20-", [20], [-1]),
            ("30,31,32,33", [30, 31, 32, 33], [1, 1, 1, 1]),
            ("30-,31,32-,33", [30, 31, 32, 33], [-1, 1, -1, 1]),
            (" 30-, 31 ,32- , 33", [30, 31, 32, 33], [-1, 1, -1, 1]),
            (
                "a-, 31 ,32- , bbb",
                [_CmdLib.ERR_PIN, 31, 32, _CmdLib.ERR_PIN],
                [_CmdLib.ERR_ANGLE_FACTOR, 1, -1, _CmdLib.ERR_ANGLE_FACTOR],
            ),
        ],
    )
    def test_parse_pinsstr(self, pins_str, pins, angle_factors):
        res_pins, res_angle_factors = _CmdLib.parse_pinsstr(pins_str)

        assert res_pins == pins
        assert res_angle_factors == angle_factors

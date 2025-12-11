import pytest

CMD = "uv run pi0servo api-client --history_file /tmp/testhist"


@pytest.mark.skip(
    reason="Cannot reliably mock pigpio in subprocess for interactive tests and API client integration"
)
class TestBasic:
    """Basic tests."""

    @pytest.mark.parametrize(
        ("in_data", "expect"),
        [
            (
                '{"method": "cancel"}\n',
                ["'status': 'ERR'", "NewConnectionError", "api-client>"],
            ),
            ("a\n", ["JSONDecodeError", "api-client>"]),
        ],
    )
    def test_api_client(self, cli_runner, in_data, expect):
        """servo command"""
        inout = {"in": in_data, "out": expect}
        cli_runner.test_interactive(CMD, in_out=inout, timeout=10.0)

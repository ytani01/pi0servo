#

import pytest

CMD = "uv run pi0servo str-client --history_file /tmp/testhist"

KEY_EOF = "\x04"


class TestBasic:
    """Basic tests."""

    def test_prepare(self, cli_runner):
        """Prepare test.
        最初の起動時に、ビルドが走って時間がかかることがあるので、
        タイムアウトを長めにして、一回目を実行
        """
        inout = {"in": "\n", "out": "> "}
        cli_runner.test_interactive(CMD, in_out=inout, timeout=20)

    @pytest.mark.parametrize(
        ("instr", "expect"),
        [
            ("\n", "str-client>"),
            ("a\n", ["error", "METHOD_NOT_FOUND", "str-client>"]),
        ],
    )
    def test_str_client(self, cli_runner, instr, expect):
        """servo command"""
        inout = {"in": instr, "out": expect}
        cli_runner.test_interactive(CMD, in_out=inout)

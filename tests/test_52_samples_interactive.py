import pytest

KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"


class TestSamplePrograms:
    """Test sample programs."""

    @pytest.mark.parametrize(
        ("sample", "inkey", "e_out"),
        [
            (
                "sample-06-onekey-cli.py 25 27 -a -1,1",
                ["j", "a", "q"],
                ["result", "angle_diffs", "JSONDecodeError"],
            ),
            (
                "sample-10-clibase.py",
                ["abc\n", "xyz\n", "exit\n"],
                ["result.data> abc", "result.data> xyz", "Aborted!"],
            ),
            (
                "sample-11-cliwithhistory.py",
                ["abc\n", "xyz\n", "exit\n"],
                ["result.data> abc", "result.data> xyz", "Aborted!"],
            ),
            (
                "sample-11-cliwithhistory.py",
                [KEY_UP, KEY_UP, KEY_UP, KEY_DOWN, "\n", "Quit\n"],
                ["result.data> xyz", "Aborted!"],
            ),
            (
                "sample-12-onekeycli.py",
                ["ab", KEY_UP, "Q"],
                ["result.data> a", "result.data> b", "result.data> KEY_UP"],
            ),
        ],
    )
    def test_sample_interactive(self, cli_runner, sample, inkey, e_out):
        """test samples."""
        cmdline = f"uv run samples/{sample}"
        print(f"* cmdline={cmdline}")
        inout = {"in": inkey, "out": e_out}
        cli_runner.test_interactive(
            cmdline, in_out=inout, terminate_flag=True, timeout=10
        )

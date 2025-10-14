import pytest


class TestSamplePrograms:
    """Test sample programs."""

    @pytest.mark.parametrize(
        ["sample", "inkey", "e_out"],
        [
            (
                "sample-06-onekey-cli.py 25 27 -a -1,1",
                ["j", "a", "q"],
                ["result", "angle_diffs", "JSONDecodeError", "QUIT"],
            ),
        ],
    )
    def test_sample_interactive(self, cli_runner, sample, inkey, e_out):
        """test samples."""
        cmdline = f"uv run samples/{sample}"
        print(f"* cmdline={cmdline}")
        inout = {"in": inkey, "out": e_out}
        cli_runner.test_interactive(
            cmdline, in_out=inout, terminate_flag=False, timeout=10
        )

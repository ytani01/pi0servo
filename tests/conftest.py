#
# (c) 2025 Yoichi Tanibayashi
#
"""
pytest conftest
"""
import os
import pty
import select
import subprocess
import time
from typing import Optional
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mocker_pigpio():
    """
    pigpio.pi()をモックするためのフィクスチャ。

    実際のpigpioライブラリの代わりに、MagicMockオブジェクトを返す。
    これにより、ハードウェア(Raspberry Pi)がない環境でも、
    pigpioに依存するコードの単体テストが可能になる。

    モックは、呼び出されたメソッドやその引数を記録するため、
    テストコードで意図した通りにメソッドが呼ばれたかを確認できる。

    使用例:
    def test_some_function(mocker_pigpio):
        # mocker_pigpioを使ってテスト対象のオブジェクトを初期化
        pi = mocker_pigpio()
        servo = PiServo(pi, 17)

        # メソッドを実行
        servo.move_center()

        # 意図した通りにメソッドが呼ばれたかを確認
        pi.set_servo_pulsewidth.assert_called_with(17, 1500)
    """
    # 'pigpio.pi'をMagicMockで置き換える
    with patch("pigpio.pi") as mock_pi_constructor:
        # pi()コンストラクタが返すインスタンスのモックを作成
        mock_pi_instance = MagicMock()

        # get_servo_pulsewidthのデフォルトの戻り値を設定
        # 具体的なテストケースで上書き可能
        mock_pi_instance.reset_mock()  # 初期化時のoff()呼び出しをクリア

        # pi()が呼ばれたら、上記で作成したインスタンスのモックを返すように設定
        mock_pi_constructor.return_value = mock_pi_instance

        # このフィクスチャを使用するテストに、
        # pi()コンストラクタのモックを渡す
        yield mock_pi_constructor


class InteractiveSession:
    def __init__(self, master_fd, process):
        self.master_fd = master_fd
        self.process = process
        self.output = ""

    def send_key(self, key: str):
        """Sends a key press to the process."""
        os.write(self.master_fd, key.encode())

    def expect(self, pattern: str, timeout: int = 5) -> bool:
        """Waits for a pattern to appear in the output."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            r, _, _ = select.select([self.master_fd], [], [], 0.1)
            if r:
                try:
                    data = os.read(self.master_fd, 1024).decode()
                    self.output += data
                    if pattern in self.output:
                        # print(f"* output: {self.output!r}")
                        print(f"* output: '''{self.output}'''")
                        print(f"* pattern: '''{pattern}'''")
                        return True
                except OSError as _e:
                    print(f"{type(_e).__name__}: {_e}")
                    break
        # print(f"* output: {self.output!r}")
        print(f"* output: '''{self.output}'''")
        print(f"* pattern: '''{pattern}'''")
        if pattern in self.output:
            return True

        self.close()
        return False

    def get_output(self) -> str:
        """Returns the captured output."""
        return self.output

    def close(self):
        """Terminates the process and closes the file descriptor."""
        self.process.terminate()
        self.process.wait()
        os.close(self.master_fd)


class CLITestBase:
    """CLIテスト用のヘルパークラス。

    コマンドの実行、出力のアサーションなど、CLIテストで頻繁に使用する機能を提供します。
    """
    DEFAULT_TIMEOUT = 10
    DEFAULT_ENCODING = "utf-8"

    def run_command(
        self,
        command: list[str],
        input_data: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        cwd: Optional[str] = None,
        env: Optional[dict[str, str]] = None,
    ) -> subprocess.CompletedProcess:
        """コマンドを実行し、結果を返します。

        Args:
            command: 実行するコマンドのリスト。
            input_data: 標準入力に渡すデータ。
            timeout: コマンドのタイムアウト（秒）。
            cwd: コマンドを実行するディレクトリ。
            env: コマンドの環境変数。
            check_success: True: コマンドが失敗したらpytest.failを呼び出す。

        Returns:
            コマンドの実行結果。

        Raises:
            pytest.fail: コマンドの実行に失敗した場合。
            pytest.skip: コマンドが見つからない場合。
        """
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding=self.DEFAULT_ENCODING,
                input=input_data,
                timeout=timeout,
                cwd=cwd,
                env=env,
            )
            return result
        except subprocess.TimeoutExpired:
            command_str = " ".join(command)
            pytest.fail(f"Command timed out after {timeout}s: {command_str}")
        except FileNotFoundError:
            pytest.fail(f"Command not found: {command[0]}")

    def run_interactive_command(
        self, command: list[str]
    ) -> "InteractiveSession":
        master_fd, slave_fd = pty.openpty()
        process = subprocess.Popen(
            command,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,
        )
        os.close(slave_fd)
        return InteractiveSession(master_fd, process)

    def assert_output_contains(
        self,
        result: subprocess.CompletedProcess,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ) -> None:
        if stdout is not None:
            assert stdout in result.stdout, (
                f"Expected '{stdout}' in stdout, got: {result.stdout!r}"
            )
        if stderr is not None:
            assert stderr in result.stderr, (
                f"Expected '{stderr}' in stderr, got: {result.stderr!r}"
            )

    def assert_output_equals(
        self,
        result: subprocess.CompletedProcess,
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
    ) -> None:
        if stdout is not None:
            assert result.stdout == stdout, (
                f"Expected stdout: {stdout!r}, got: {result.stdout!r}"
            )
        if stderr is not None:
            assert result.stderr == stderr, (
                f"Expected stderr: {stderr!r}, got: {result.stderr!r}"
            )

    def assert_return_code(
        self, result: subprocess.CompletedProcess, expected: int
    ) -> None:
        assert result.returncode == expected, (
            f"Expected return code {expected}, got {result.returncode}\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )


@pytest.fixture
def cli_runner():
    """CLI テスト基盤を fixture として提供（インスタンスを返す）"""
    return CLITestBase()


# Key Constants for Interactive Testing
KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"
KEY_RIGHT = "\x1b[C"
KEY_LEFT = "\x1b[D"
KEY_ENTER = "\n"

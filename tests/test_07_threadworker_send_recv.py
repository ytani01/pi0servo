#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_07_threadworker.py
"""

from unittest.mock import MagicMock, patch

import pytest
import time # 追加

from pi0servo.core.multi_servo import MultiServo
from pi0servo.helper.thread_worker import ThreadWorker

PINS = [17, 18]


@pytest.fixture
def mocker_multiservo():
    """MultiServoをモックするためのフィクスチャ"""
    with patch(
        "pi0servo.helper.thread_worker.MultiServo"
    ) as mock_mservo_constructor:
        mock_mservo_instance = MagicMock(spec=MultiServo)
        mock_mservo_constructor.return_value = mock_mservo_instance
        yield mock_mservo_constructor


@pytest.fixture
def thread_worker(mocker_multiservo, mocker_pigpio):
    """ThreadWorkerのテスト用インスタンスを生成するフィクスチャ"""
    pi = mocker_pigpio()
    mock_mservo_instance = mocker_multiservo.return_value
    worker = ThreadWorker(pi, PINS, debug=False)
    worker.start()  # スレッドを開始
    yield worker, mock_mservo_instance
    worker.end()  # テスト終了時にスレッドを終了


class TestThreadWorker:
    """ThreadWorkerクラスのテスト"""

    def test_send_get_all_angles_query(self, thread_worker):
        """get_all_anglesクエリコマンドのテスト"""
        worker, mock_mservo_instance = thread_worker
        expected_angles = [10.0, 20.0]
        mock_mservo_instance.get_all_angles.return_value = expected_angles

        cmd = {"method": "get_all_angles"}
        reply = worker.send(cmd)

        mock_mservo_instance.get_all_angles.assert_called_once()
        assert reply["result"]["value"] == expected_angles
        assert reply["result"]["qsize"] == 0

    def test_send_wait_after_async_command(self, thread_worker):
        """非同期コマンド送信後のwaitコマンドテスト"""
        worker, mock_mservo_instance = thread_worker
        
        # MServoのメソッドが呼ばれるまで待つヘルパー関数を定義
        def wait_for_mservo_call(mock_call, timeout=1.0, interval=0.01):
            start_time = time.time()
            while time.time() - start_time < timeout:
                if mock_call.called:
                    return
                time.sleep(interval)
            raise TimeoutError(f"MServo method {mock_call} not called within {timeout}s")
        
        cmd_async = {"method": "move_all_angles_sync", "params": {"angles": [0,0]}}
        cmd_wait = {"method": worker.CMD_WAIT}

        # 非同期コマンドを送信
        reply_async = worker.send(cmd_async)
        assert reply_async["result"]["qsize"] == 1 # キューにコマンドがある
        
        # MServoのメソッドが呼び出されるのを待つ
        wait_for_mservo_call(mock_mservo_instance.move_all_angles_sync)

        # waitコマンドを送信
        reply_wait = worker.send(cmd_wait)

        # waitコマンドが処理完了を待ち、最終的なqsizeが0であることを確認
        assert reply_wait["result"]["value"] == 0
        assert reply_wait["result"]["qsize"] == 0
        mock_mservo_instance.move_all_angles_sync.assert_called_once_with([0,0], worker.move_sec, worker.step_n)




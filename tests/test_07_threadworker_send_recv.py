#
# (c) 2025 Yoichi Tanibayashi
#
"""
tests/test_07_threadworker.py
"""

from unittest.mock import MagicMock, patch

import pytest

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
    mocker_multiservo()
    worker = ThreadWorker(pi, PINS, debug=False)
    yield worker


class TestThreadWorker:
    """ThreadWorkerクラスのテスト"""

    @pytest.mark.parametrize(
        ["json_data"],
        [
            ({"method": "move", "params": {"angles": [10, 10]}},),
            # (
            #     [{"method": "move", "params": {"angles": [10,10]}}],
            # ),
            # (
            #     [
            #         {"method": "move", "params": {"angles": [10,10]}},
            #         {"method": "move", "params": {"angles": [-10,-10]}}
            #     ],
            # ),
        ],
    )
    def test_init(self, thread_worker, json_data):
        """初期化のテスト"""
        print(f"\njson_data={json_data}")

        thread_worker.send(json_data)

        recv_data = thread_worker.recv()
        print(f"recv_data={recv_data}")

        assert recv_data == json_data

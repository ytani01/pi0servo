#
# (c) 2025 Yoichi Tanibayashi
#
"""PigpioClient class."""

import pigpio

from ..base.base_component import BaseComponent


class PigpioClient(BaseComponent):
    """pigpio.pi()をラップし、抽象的なインターフェースを提供するクラス。"""

    def __init__(self, debug: bool = False):
        """コンストラクタ"""
        super().__init__(debug)
        self.pi = pigpio.pi()
        if not self.pi.connected:
            self._log.error("pigpio daemon not connected.")
            raise ConnectionError("pigpio daemon not connected.")

    def set_servo_pulsewidth(self, pin: int, pulsewidth: int):
        """サーボのパルス幅を設定する。"""
        self.pi.set_servo_pulsewidth(pin, pulsewidth)

    def get_servo_pulsewidth(self, pin: int) -> int:
        """サーボのパルス幅を取得する。"""
        return self.pi.get_servo_pulsewidth(pin)

    def stop(self):
        """pigpioを停止する。"""
        self.pi.stop()

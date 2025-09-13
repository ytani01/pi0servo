#
# (c) 2025 Yoichi Tanibayashi
#
"""IServoController interface."""

from abc import ABC, abstractmethod
from typing import List, Optional


class IServoController(ABC):
    """
    サーボモーターを制御するための抽象インターフェース。
    """

    @property
    @abstractmethod
    def pins(self) -> List[int]:
        """サーボが接続されているGPIOピンのリスト。"""
        pass

    @property
    @abstractmethod
    def conf_file(self) -> str:
        """使用している設定ファイルのパス。"""
        pass

    @abstractmethod
    def get_all_pulses(self) -> List[int]:
        """すべてのサーボの現在のパルス幅を取得する。"""
        pass

    @abstractmethod
    def get_all_angles(self) -> List[float]:
        """すべてのサーボの現在の角度を取得する。"""
        pass

    @abstractmethod
    def move_all_angles(self, target_angles: List[Optional[float]]):
        """すべてのサーボを指定された角度に移動させる。"""
        pass

    @abstractmethod
    def move_all_angles_sync(
        self,
        target_angles: List[Optional[float]],
        move_sec: Optional[float] = None,
        step_n: Optional[int] = None,
    ):
        """すべてのサーボを目標角度まで同期的かつ滑らかに動かす。"""
        pass

    @abstractmethod
    def move_all_angles_sync_relative(
        self,
        angle_diffs: List[Optional[float]],
        move_sec: Optional[float] = None,
        step_n: Optional[int] = None,
    ):
        """現在の角度からの相対角度で、滑らかに移動する。"""
        pass

    @abstractmethod
    def off(self):
        """すべてのサーボをオフにする。"""
        pass
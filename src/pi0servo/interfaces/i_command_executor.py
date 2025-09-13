#
# (c) 2025 Yoichi Tanibayashi
#
"""ICommandExecutor interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class ICommandExecutor(ABC):
    """
    コマンドを実行するための抽象インターフェース。
    """

    @abstractmethod
    def send(self, cmd_data: Dict[str, Any]):
        """コマンドデータを実行キューに送信する。"""
        pass

    @abstractmethod
    def clear_cmdq(self) -> int:
        """コマンドキューをクリアする。"""
        pass

    @abstractmethod
    def end(self):
        """コマンド実行器を終了する。"""
        pass

    @abstractmethod
    def start(self):
        """コマンド実行器を開始する。"""
        pass

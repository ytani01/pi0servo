#
# (c) 2025 Yoichi Tanibayashi
#
"""BaseComponent for common initialization."""

from ..utils.my_logger import get_logger


class BaseComponent:
    """
    共通の初期化ロジック（デバッグフラグとロガー）を提供する基底クラス。
    """
    def __init__(self, debug: bool = False):
        self._debug = debug
        self.__log = get_logger(self.__class__.__name__, self._debug)
        self.__log.debug("BaseComponent initialized.")

    @property
    def debug(self) -> bool:
        return self._debug

    @property
    def _log(self):
        return self.__log

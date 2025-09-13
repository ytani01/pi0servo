#
# (c) 2025 Yoichi Tanibayashi
#
"""ErrorCode Enum."""

from enum import Enum


class ErrorCode(Enum):
    """Error Code."""
    UNKNOWN_COMMAND = 1
    INVALID_PARAMETER = 2
    INVALID_JSON = 3

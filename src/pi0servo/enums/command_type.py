#
# (c) 2025 Yoichi Tanibayashi
#
"""CommandType Enum."""

from enum import Enum


class CommandType(Enum):
    """Command Type."""
    MOVE_ALL_ANGLES_SYNC = "move_all_angles_sync"
    MOVE_ALL_ANGLES_SYNC_RELATIVE = "move_all_angles_sync_relative"
    MOVE_ALL_ANGLES = "move_all_angles"
    SLEEP = "sleep"
    MOVE_SEC = "move_sec"
    STEP_N = "step_n"
    INTERVAL = "interval"
    MOVE_ALL_PULSES_RELATIVE = "move_all_pulses_relative"
    SET = "set"
    CANCEL = "cancel"
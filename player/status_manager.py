"""Status management for the player."""

from typing import Optional, TypeVar, Union
from utils.types import StatusType
# 延迟导入以避免循环导入
def get_game_state():
    from engine.game_state import game_state
    return game_state

class StatusManager:
    """Manages the player's status."""

    def __init__(self, initial_status: StatusType = StatusType.NEUTRAL) -> None:
        self._status = initial_status

    @property
    def status(self) -> StatusType:
        return self._status

    @status.setter
    def status(self, value: StatusType) -> None:
        self._status = StatusType.NEUTRAL

    def change_to_status(self, new_status: StatusType) -> None:
        """Change the player's status to a new status."""
        if self._status == new_status:
            return
        if self._status == StatusType.CALM: # gain 2 energy when leaving Calm
            player = get_game_state().player
            player.energy += 2
        if self._status == StatusType.DIVINITY: # gain 3 energy when entering Divinity
            player = get_game_state().player
            player.energy += 3
        self._status = new_status
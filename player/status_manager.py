"""Status management for the player."""

from utils.types import StatusType


class StatusManager:
    """Manages the player's combat stance."""

    def __init__(self, initial_status: StatusType = StatusType.NEUTRAL) -> None:
        self._status = initial_status

    @property
    def status(self) -> StatusType:
        return self._status

    @status.setter
    def status(self, value: StatusType) -> None:
        self._status = value

    def change_to_status(self, new_status: StatusType) -> None:
        self._status = new_status

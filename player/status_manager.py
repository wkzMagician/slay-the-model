"""Status management for the player."""

from typing import Optional, TypeVar, Union

Status = TypeVar('Status')
StatusType = str


class StatusManager:
    """Manages the player's status."""

    def __init__(self, initial_status: str = "Calm") -> None:
        self._status = initial_status

    @property
    def status(self) -> str:
        return self._status

    @status.setter
    def status(self, value: str) -> None:
        # Validate status is a non-empty string
        if isinstance(value, str) and value.strip():
            self._status = value.strip()
        else:
            self._status = "Calm"  # Default if invalid

    def set_status(self, status: Union[Status, StatusType]) -> None:
        """Set player's status."""
        self.status = str(status)

    def is_status(self, status: str) -> bool:
        """Check if player has specific status."""
        return self._status.lower() == status.lower()

    def reset_to_calm(self) -> None:
        """Reset status to calm."""
        self.status = "Calm"

    def get_status_effect(self) -> Optional[any]:
        """Get effect associated with current status (placeholder)."""
        # Status effects would typically be defined in a registry
        return None
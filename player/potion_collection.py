from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from player.player import Player


class PotionCollection(list):
    def __init__(self, owner: "Player", *args):
        super().__init__(*args)
        self._owner = owner

    def _within_limit(self) -> bool:
        return len(self) < self._owner.potion_limit

    def append(self, potion) -> bool:  # type: ignore[override]
        if not self._within_limit():
            return False
        super().append(potion)
        return True

    def extend(self, iterable) -> None:  # type: ignore[override]
        for item in iterable:
            if not self.append(item):
                break

    def insert(self, index: int, potion) -> None:  # type: ignore[override]
        if not self._within_limit():
            return
        super().insert(index, potion)

    def trim_to_limit(self) -> None:
        limit = self._owner.potion_limit
        if limit < 0:
            return
        if len(self) > limit:
            del self[limit:]
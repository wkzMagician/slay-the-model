"""
Rare Global Relics
Global relics available to all characters at rare rarity.
"""
from typing import List
from actions.base import Action
from relics.base import Relic
from utils.types import CardType, RarityType
from utils.registry import register

@register("relic")
class BirdFacedUrn(Relic):
    """Whenever you play a Power card, heal 2 HP."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_play(self, card, player, entities) -> List[Action]:
        if card.card_type == CardType.POWER:
            from actions.combat import HealAction
            return [HealAction(target=player, amount=2)]
        return []


@register("tiny_chest")
class TinyChest(Relic):
    """Every 4th ? room is a Treasure room."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE
        self.unknown_room_count = 0

    def on_map_enter(self, map_data) -> List[Action]:
        """Track number of unknown rooms visited."""
        from engine.game_state import game_state
        self.unknown_room_count += 1

        # Every 3rd ? room is Treasure (forces treasure room)
        if self.unknown_room_count % 3 == 0:
            # Force treasure room
            from utils.result_types import NoneResult
            from engine.game_state import game_state
            game_state.unknown_room_visits[RoomType.TREASURE] = 0
            # Reset counter after triggering
            self.unknown_room_count = 0

        return []

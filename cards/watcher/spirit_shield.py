from actions.combat import GainBlockAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class SpiritShield(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 2
    base_magic = {"per_card": 3}
    upgrade_magic = {"per_card": 4}
    text_name = "Spirit Shield"
    text_description = "Gain Block equal to {magic.per_card} for each card in your hand."

    @property
    def block(self) -> int:
        hand = game_state_module.game_state.player.card_manager.get_pile("hand")
        return len(hand) * self.get_magic_value("per_card")

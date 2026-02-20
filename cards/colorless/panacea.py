"""
Colorless Uncommon Skill card - Panacea
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Panacea(Card):
    """Gain Artifact, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"artifact": 1}
    base_exhaust = True

    upgrade_magic = {"artifact": 2}

    def on_play(self, targets: List[Creature] = []) -> List[Action]:
        target = targets[0] if targets else None
        from engine.game_state import game_state

        actions = super().on_play(targets)

        # Gain Artifact
        artifact_amount = self.get_magic_value("artifact")
        actions.append(ApplyPowerAction(
            power="Artifact",
            target=game_state.player,
            amount=artifact_amount
        ))

        return actions

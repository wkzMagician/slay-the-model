"""
Common Global Relics
Global relics available to all characters at common rarity.
"""
from typing import List
from actions.base import Action, LambdaAction
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register

@register("relic")
class Akabeko(Relic):
    """Your first Attack each combat deals 8 additional damage"""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

        # Track if first attack has been played this combat
        self.first_attack_played = False

    def on_combat_start(self, player, entities) -> List[Action]:
        """Reset first attack tracker at start of combat"""
        return [LambdaAction(func=lambda: setattr(self, 'first_attack_played', False))]
    
    # todo: 怎么应用攻击加成

@register("relic")
class Anchor(Relic):
    """Gain 10 Block at start of the first turn of each combat"""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
    
    def on_player_turn_start(self, player, entities) -> List[Action]:
        # 第一回合，获得10点格挡
        from engine.game_state import game_state
        if game_state.combat_state.combat_turn == 1:
            from actions.combat import GainBlockAction
            return [GainBlockAction(block=10)]
        return []

@register("relic")
class AncientTeaSet(Relic):
    """Start each combat with 1 extra Energy"""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON
        self.is_rest_last_room = False

    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 1 extra Energy at start of combat"""
        from actions.combat import GainEnergyAction
        if self.is_rest_last_room:
            self.is_rest_last_room = False  # Reset flag after use
            return [GainEnergyAction(energy=1)]
        return []

@register("relic")
class BagOfPreparation(Relic):
    """At the start of each combat, draw 2 additional cards."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, player, entities) -> List[Action]:
        """Draw 2 additional cards at the start of combat"""
        from actions.card import DrawCardsAction
        return [DrawCardsAction(count=2)]


@register("relic")
class Vajra(Relic):
    """Gain 1 Strength at start of combat"""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, player, entities) -> List[Action]:
        """Gain 1 Strength at start of combat"""
        from actions.combat import ApplyPowerAction
        # todo: from powers.strength import StrengthPower
        return [ApplyPowerAction(power=StrengthPower(amount=1))]
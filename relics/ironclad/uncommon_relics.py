"""Uncommon Ironclad relics."""
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


@register("relic")
class BagOfPreparation(Relic):
    """Draw cards at start of combat"""
    rarity = RarityType.UNCOMMON

    def on_combat_start(self, player, entities):
        """Draw 3 cards at start of combat"""
        from actions.combat import DrawCards
        DrawCards(amount=3).execute(player, entities)


@register("relic")
class WhiteBeastStatue(Relic):
    """Enemies spawn with less HP"""
    rarity = RarityType.UNCOMMON

    def on_combat_start(self, player, entities):
        """Reduce all enemies' max HP by 1 at start of combat"""
        for entity in entities:
            if hasattr(entity, 'max_hp') and hasattr(entity, 'hp'):
                entity.max_hp = max(1, entity.max_hp - 1)
                entity.hp = min(entity.hp, entity.max_hp)


@register("relic")
class Medalkit(Relic):
    """Heal HP at start of combat"""
    rarity = RarityType.UNCOMMON

    def on_combat_start(self, player, entities):
        """Heal 3 HP at start of combat"""
        from actions.health import Heal
        Heal(amount=3).execute(player, entities)


@register("relic")
class PaperKite(Relic):
    """Draw cards each turn"""
    rarity = RarityType.UNCOMMON

    def on_player_turn_start(self, player, entities):
        """Draw 2 cards at start of each player turn"""
        from actions.combat import DrawCards
        DrawCards(amount=2).execute(player, entities)


@register("relic")
class WristBlade(Relic):
    """Gain Strength at end of combat"""
    rarity = RarityType.UNCOMMON

    def on_combat_end(self, player, entities):
        """Gain 3 Strength at end of combat"""
        from actions.combat import AddStrength
        AddStrength(amount=3).execute(player, entities)

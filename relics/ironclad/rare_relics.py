"""Rare Ironclad relics."""
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


@register("relic")
class SneckoEye(Relic):
    """Enemies start with less HP"""
    rarity = RarityType.RARE

    def on_combat_start(self, player, entities):
        """Reduce all enemies' max HP by 3 at start of combat"""
        for entity in entities:
            if hasattr(entity, 'max_hp') and hasattr(entity, 'hp'):
                entity.max_hp = max(1, entity.max_hp - 3)
                entity.hp = min(entity.hp, entity.max_hp)


@register("relic")
class SlaversCage(Relic):
    """Gain Strength each combat"""
    rarity = RarityType.RARE

    def on_combat_start(self, player, entities):
        """Gain 2 Strength at start of combat"""
        from actions.combat import AddStrength
        AddStrength(amount=2).execute(player, entities)


@register("relic")
class PaperFrog(Relic):
    """Draw cards when HP drops below 50%"""
    rarity = RarityType.RARE

    def __init__(self):
        super().__init__()
        self.triggered_this_combat = False

    def on_damage_taken(self, damage, source, player, entities):
        """When HP drops below 50%, draw 2 cards"""
        if not self.triggered_this_combat:
            hp_percent = player.hp / player.max_hp if player.max_hp > 0 else 0
            if hp_percent < 0.5:
                from actions.combat import DrawCards
                DrawCards(amount=2).execute(player, entities)
                self.triggered_this_combat = True

    def on_combat_end(self, player, entities):
        """Reset trigger flag at end of combat"""
        self.triggered_this_combat = False


@register("relic")
class MoltenEgg(Relic):
    """+1 Energy every turn"""
    rarity = RarityType.RARE

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each player turn"""
        from actions.combat import GainEnergy
        GainEnergy(amount=1).execute(player, entities)


@register("relic")
class ChampionsBelt(Relic):
    """Cards cost 0 every 5th card"""
    rarity = RarityType.RARE

    def __init__(self):
        super().__init__()
        self.cards_played_this_combat = 0

    def on_card_play(self, card, player, entities):
        """Every 5th card costs 0 this turn"""
        self.cards_played_this_combat += 1
        if self.cards_played_this_combat % 5 == 0:
            # Make the next card cost 0 this turn
            # Note: This is a simplified implementation
            # Full implementation would require card cost modification
            pass

    def on_combat_end(self, player, entities):
        """Reset counter at end of combat"""
        self.cards_played_this_combat = 0

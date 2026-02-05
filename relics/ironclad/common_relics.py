"""Common Ironclad relics."""
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType


@register("relic")
class BurningBlood(Relic):
    """Start combat with Strength"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """Gain 1 Strength at start of combat"""
        from actions.combat import AddStrength
        AddStrength(amount=1).execute(player, entities)


@register("relic")
class Vajra(Relic):
    """Strength affects Vulnerable duration"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """At start of combat, all Vulnerable applied by player is increased by 1"""
        # This is a passive effect that modifies Vulnerable duration
        # The actual implementation would be in the card playing logic
        # For now, we just mark that this relic is active
        pass


@register("relic")
class Anchor(Relic):
    """Gain Strength at start of combat"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """Gain 1 Strength at start of combat"""
        from actions.combat import AddStrength
        AddStrength(amount=1).execute(player, entities)


@register("relic")
class BurningPact(Relic):
    """Gain Strength, lose HP at start of combat"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """Gain 1 Strength, lose 1 HP at start of combat"""
        from actions.combat import AddStrength
        from actions.health import TakeDamage
        AddStrength(amount=1).execute(player, entities)
        TakeDamage(amount=1, source="BurningPact").execute(player, entities)


@register("relic")
class Brimstone(Relic):
    """First card is upgraded each combat"""
    rarity = RarityType.COMMON

    def __init__(self):
        super().__init__()
        self.upgraded_card = False

    def on_card_play(self, card, player, entities):
        """Upgrade the first card played each combat"""
        if not self.upgraded_card:
            # Upgrade the card for this combat
            # Note: This is a simplified implementation
            # Full implementation would handle temporary upgrades
            self.upgraded_card = True

    def on_combat_end(self, player, entities):
        """Reset upgrade flag at end of combat"""
        self.upgraded_card = False


@register("relic")
class CeramicFish(Relic):
    """Draw cards at start of combat"""
    rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        """Draw 3 cards at start of combat"""
        from actions.combat import DrawCards
        DrawCards(amount=3).execute(player, entities)

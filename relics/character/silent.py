"""Silent-specific relics."""
from engine.runtime_api import add_actions

from actions.base import LambdaAction
from actions.card import AddCardAction, DrawCardsAction
from actions.combat import ApplyPowerAction, DealDamageAction, GainBlockAction, GainEnergyAction
from cards.colorless.shiv import Shiv
from powers.definitions.poison import PoisonPower
from relics.base import Relic
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import RarityType, CardType


@register("relic")
class RingOfTheSnake(Relic):
    """At the start of each combat, draw 2 additional cards."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_combat_start(self, player, entities):
        add_actions([DrawCardsAction(count=2)])
        return


@register("relic")
class SneckoSkull(Relic):
    """Whenever you apply Poison, apply an additional 1 Poison."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.COMMON

    def on_apply_power(self, power, target, player, entities):
        if isinstance(power, PoisonPower):
            applied_poison = target.get_power("Poison")
            if applied_poison is not None:
                applied_poison.amount += 1
        return


@register("relic")
class NinjaScroll(Relic):
    """Start each combat with 3 Shivs in hand."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_combat_start(self, player, entities):
        add_actions([
            AddCardAction(card=Shiv(), dest_pile="hand")
            for _ in range(3)
        ])
        return


@register("relic")
class PaperKrane(Relic):
    """Enemies with Weak deal 50% less damage rather than 25%."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.damage_phase = DamagePhase.MULTIPLICATIVE

    def modify_damage_taken(self, base_damage: int, source=None) -> int:
        if source and hasattr(source, "powers"):
            for power in source.powers:
                if getattr(power, "name", "") == "Weak":
                    return int(base_damage * 4 / 5)
        return base_damage


@register("relic")
class TheSpecimen(Relic):
    """Whenever an enemy dies, transfer any Poison it has to a random enemy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_damage_dealt(self, damage, target, player, entities):
        if target.is_dead():
            poison_amount = 0
            for power in target.powers:
                if power.idstr == "PoisonPower":
                    poison_amount = power.amount
                    break
            if poison_amount > 0:
                alive_enemies = [enemy for enemy in entities if not enemy.is_dead()]
                if alive_enemies:
                    import random

                    target_enemy = random.choice(alive_enemies)
                    add_actions([
                        ApplyPowerAction(power="Poison", target=target_enemy, amount=poison_amount)
                    ])
        return


@register("relic")
class Tingsha(Relic):
    """Whenever you discard a card during your turn, deal 3 damage to a random enemy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card, player, entities):
        from engine.game_state import game_state

        assert game_state.current_combat is not None
        alive_enemies = [enemy for enemy in game_state.current_combat.enemies if not enemy.is_dead()]
        if alive_enemies:
            import random

            target_enemy = random.choice(alive_enemies)
            add_actions([DealDamageAction(damage=3, target=target_enemy)])
        return


@register("relic")
class ToughBandages(Relic):
    """Whenever you discard a card during your turn, gain 3 Block."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.RARE

    def on_card_discard(self, card, player, entities):
        add_actions([GainBlockAction(block=3, target=player)])
        return


@register("relic")
class HoveringKite(Relic):
    """The first time you discard a card each turn, gain 1 Energy."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.discarded_this_turn = False

    def on_combat_start(self, player, entities):
        add_actions([LambdaAction(func=lambda: setattr(self, "discarded_this_turn", False))])
        return

    def on_card_discard(self, card, player, entities):
        if not self.discarded_this_turn:
            self.discarded_this_turn = True
            add_actions([GainEnergyAction(energy=1)])
        return


@register("relic")
class RingOfTheSerpent(Relic):
    """Replaces Ring of the Snake. At the start of your turn, draw 1 additional card."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        add_actions([DrawCardsAction(count=1)])
        return


@register("relic")
class WristBlade(Relic):
    """Attacks that cost 0 Energy deal 4 additional damage."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        if card and getattr(card, "card_type", None) == CardType.ATTACK and getattr(card, "cost", None) == 0:
            return base_damage + 4
        return base_damage


@register("relic")
class TwistedFunnel(Relic):
    """At the start of each combat, apply 4 Poison to all enemies."""

    def __init__(self):
        super().__init__()
        self.rarity = RarityType.SHOP

    def on_combat_start(self, player, entities):
        add_actions([
            ApplyPowerAction(power="Poison", target=enemy, amount=4, duration=3)
            for enemy in entities
        ])
        return

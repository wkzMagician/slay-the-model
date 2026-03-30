"""
Boss Global Relics
Global relics available at boss rarity.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action, LambdaAction
from actions.card import AddCardAction, ChooseRemoveCardAction, DrawCardsAction, TransformCardAction, ChooseTransformAndUpgradeAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction
from powers.definitions.confused import ConfusedPower
from powers.definitions.strength import StrengthPower
from cards.colorless.curse_of_the_bell import CurseOfTheBell
from cards.colorless.wound import Wound
from relics.base import Relic
from utils.types import CombatType, PilePosType, RarityType, CardType
from utils.registry import register
from utils.random import get_random_card

# NOTE: AddRandomRelicAction must be imported lazily inside methods
# to avoid circular import between actions.reward -> relics.base -> relics.global_relics.boss

@register("relic")
class SneckoEye(Relic):
    """Draw 2 additional cards each turn. Start each combat Confused."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_combat_start(self, player, entities):
        """Start each combat confused"""
        from engine.game_state import game_state
        add_actions([ApplyPowerAction(ConfusedPower(amount=0, owner=player), player)])
        return
    def on_player_turn_start(self, player, entities):
        """Draw 2 additional cards at start of turn"""
        from engine.game_state import game_state
        add_actions([DrawCardsAction(count=2)])
        return
@register("relic")
class Astrolabe(Relic):
    """Upon pickup, choose and Transform 3 Cards, then Upgrade them."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ChooseTransformAndUpgradeAction(pile="deck", amount=3)])
        return
@register("relic")
class BlackStar(Relic):
    """Elites drop an additional Relic when defeated."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_elite_victory(self, player, entities):
        """Drop an additional random relic when defeating an elite."""
        from actions.reward import AddRandomRelicAction
        from engine.game_state import game_state
        add_actions([AddRandomRelicAction()])
        return
@register("relic")
class BlackBlood(Relic):
    """Replaces Burning Blood. At the end of combat, heal 12 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_combat_end(self, player, entities):
        """Heal 12 HP at combat end"""
        from engine.game_state import game_state
        add_actions([HealAction(amount=12)])
        return
@register("relic")
class BustedCrown(Relic):
    """Gain 1 Energy at start of each turn. On Card Reward screens, you have 2 fewer Cards to choose from."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
@register("relic")
class CallingBell(Relic):
    """Upon pickup, obtain a unique Curse and 3 Relics."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        
    def on_obtain(self):
        # Lazy import to avoid circular dependency
        from actions.reward import AddRandomRelicAction
        from engine.game_state import game_state
        add_actions(
        [
            AddCardAction(CurseOfTheBell(), "deck"),
            AddRandomRelicAction([RarityType.COMMON]),
            AddRandomRelicAction([RarityType.UNCOMMON]),
            AddRandomRelicAction([RarityType.RARE])
        ]
        )
        return

@register("relic")
class CoffeeDripper(Relic):
    """Gain 1 Energy at start of each turn. You can no longer Rest at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    # Implement logic in RestRoom

@register("relic")
class CursedKey(Relic):
    """Gain 1 Energy at start of each turn. Whenever you open a non-boss chest, obtain a Curse."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    def on_chest_open(self, chest_type: str | None = None):
        """Gain a Curse when opening a non-boss chest."""
        if chest_type == "boss":
            return
        curse = get_random_card(
            namespaces=["colorless"],
            card_types=[CardType.CURSE],
            rarities=[RarityType.CURSE],
        )
        if curse is None:
            return
        from engine.game_state import game_state
        add_actions([AddCardAction(curse, "deck")])
        return
@register("relic")
class Ectoplasm(Relic):
    """Gain 1 Energy at start of each turn. You can no longer gain Gold."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
@register("relic")
class EmptyCage(Relic):
    """Upon pickup, remove 2 Cards from your Deck."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ChooseRemoveCardAction("deck", 2)])
        return
@register("relic")
class FusionHammer(Relic):
    """Gain 1 Energy at start of each turn. You can no longer Smith at Rest Sites."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    # Implement logic in RestRoom

@register("relic")
class MarkOfPain(Relic):
    """Gain 1 Energy at start of each turn. Start combats with 2 Wounds in your Drawpile."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
        self.wounds_added = False

    def on_combat_start(self, player, entities):
        """Add Wounds to draw pile at combat start"""
        from engine.game_state import game_state
        add_actions([AddCardAction(Wound(), "draw_pile", pos=PilePosType.RANDOM) * 2])
        return
    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
@register("relic")
class PandorasBox(Relic):
    """Transform all Strikes and Defends."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self):
        actions = []
        from engine.game_state import game_state
        namespace = game_state.player.namespace
        for card in game_state.player.card_manager.get_pile('deck'):
            if card.idstr == f"{namespace}.Attack" or card.idstr == f"{namespace}.Defend":
                actions.append(TransformCardAction(card, 'deck'))
        from engine.game_state import game_state
        add_actions(actions)
        return
@register("relic")
class PhilosophersStone(Relic):
    """Gain 1 Energy at start of each turn. ALL enemies start with 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    def on_combat_start(self, player, entities):
        actions = []
        from engine.game_state import game_state
        assert game_state.current_combat is not None
        for enemy in game_state.current_combat.enemies:
            if enemy.hp > 0:
                actions.append(ApplyPowerAction(StrengthPower(amount=1, owner=enemy), enemy))

        from engine.game_state import game_state

        add_actions(actions)

        return
@register("relic")
class RunicCube(Relic):
    """Whenever you lose HP, draw 1 card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_damage_taken(self, damage, source, player, entities):
        """Draw 1 card when taking damage"""
        if damage > 0:
            from engine.game_state import game_state
            add_actions([DrawCardsAction(count=1)])
            return
        return
@register("relic")
class RunicDome(Relic):
    """Gain 1 Energy at start of each turn. You can no longer see enemy Intents."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    # Hidden intent logic implemented in engine/combat.py:
    # - _print_combat_state(): skips printing intention info
    # - execute_enemy_phase(): skips printing "Enemy intends to" message

@register("relic")
class RunicPyramid(Relic):
    """At the end of your turn, you no longer discard your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    # Implemented in engine/combat.py - hand discard is skipped if player has this relic

@register("relic")
class SacredBark(Relic):
    """Double effectiveness of most Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    # Implement in potion

@register("relic")
class SlaversCollar(Relic):
    """During Boss and Elite combats, gain 1 Energy at the start of your turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        # Get current combat
        from engine.game_state import game_state
        combat = game_state.current_combat
        assert combat is not None
        if combat.combat_type != CombatType.NORMAL:
            from engine.game_state import game_state
            add_actions([GainEnergyAction(energy=1)])
            return
        return
@register("relic")
class Sozu(Relic):
    """Gain 1 Energy at start of each turn. You can no longer obtain Potions."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain 1 Energy at start of each turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
@register("relic")
class TinyHouse(Relic):
    """Obtain 1 Potion. Gain 50 Gold. Raise your Max HP by 5. Obtain 1 Card. Upgrade 1 Random Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS
    
    def on_obtain(self):
        from actions.reward import AddRandomPotionAction, AddGoldAction
        from actions.combat import ModifyMaxHpAction
        from actions.card import ChooseObtainCardAction, UpgradeRandomCardAction
        from engine.game_state import game_state
        
        from engine.game_state import game_state
        add_actions(
        [
            AddRandomPotionAction(game_state.player.namespace),
            AddGoldAction(amount=50),
            ModifyMaxHpAction(amount=5),
            ChooseObtainCardAction(total=3, namespace=game_state.player.namespace, encounter_type="noraml", use_rolling_offset=True),
            UpgradeRandomCardAction(count=1, namespace=game_state.player.namespace)
        ]
        )
        return

@register("relic")
class VelvetChoker(Relic):
    """Gain 1 Energy at start of each turn. You cannot play more than 6 Cards per turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.BOSS

    def on_player_turn_start(self, player, entities):
        """Gain Energy at start of turn"""
        from engine.game_state import game_state
        add_actions([GainEnergyAction(energy=1)])
        return
    # Card play limit implemented in Card.can_play() in cards/base.py
    # Checks combat_state.turn_cards_played >= 6 and blocks further card plays


"""
Uncommon Global Relics
Global relics available to all characters at uncommon rarity.
"""
from engine.runtime_api import add_action, add_actions
from typing import List
from actions.base import Action, LambdaAction
from actions.card import DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction, HealAction, DealDamageAction, ApplyPowerAction, ModifyMaxHpAction
# GainGoldAction imported lazily when needed to avoid circular import
from actions.misc import BottledCardInputRequestAction
from relics.base import Relic
from utils.types import RarityType, CardType, PilePosType
from utils.registry import register
from utils.damage_phase import DamagePhase

# Existing relic
@register("relic")
class HornCleat(Relic):
    """At the start of your 2nd turn, gain 14 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_player_turn_start(self, player, entities):
        """At the start of your 2nd turn, gain 14 Block."""
        from engine.game_state import game_state
        if game_state.current_combat is not None:
            if game_state.current_combat.combat_state.combat_turn == 2:
                from engine.game_state import game_state
                add_actions([GainBlockAction(block=14, target=player)])
                return
        return
# New Uncommon relics
@register("relic")
class BlueCandle(Relic):
    """Curse Cards can now be played. Playing a Curse will make you lose 1 HP and Exhaust Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def can_play_curse_cards(self) -> bool:
        """Allow Curse cards to be played."""
        return True

    def should_exhaust_curse_on_play(self) -> bool:
        """Played Curse cards should exhaust."""
        return True

    def curse_play_hp_loss(self) -> int:
        """HP loss when a Curse is played."""
        return 1


@register("relic")
class BottledFlame(Relic):
    """Upon pick up, choose an Attack. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None

    def on_obtain(self):
        """Choose an Attack card when this relic is obtained."""
        from engine.game_state import game_state
        add_actions([BottledCardInputRequestAction(self, CardType.ATTACK)])
        return
    def on_combat_start(self, player, entities):
        """Add selected card to hand at start of combat."""
        if self.selected_card:
            # Add a copy of selected card to hand
            from actions.card import AddCardAction
            from engine.game_state import game_state
            add_actions([AddCardAction(card=self.selected_card, dest_pile='hand', position=PilePosType.TOP)])
            return
        return
@register("relic")
class BottledLightning(Relic):
    """Upon pick up, choose a Skill. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None

    def on_obtain(self):
        """Choose a Skill card when this relic is obtained."""
        from engine.game_state import game_state
        add_actions([BottledCardInputRequestAction(self, CardType.SKILL)])
        return
    def on_combat_start(self, player, entities):
        """Add selected card to hand at start of combat."""
        if self.selected_card:
            # Add a copy of selected card to hand
            from actions.card import AddCardAction
            from engine.game_state import game_state
            add_actions([AddCardAction(card=self.selected_card, dest_pile='hand', position=PilePosType.TOP)])
            return
        return
@register("relic")
class BottledTornado(Relic):
    """Upon pick up, choose a Power. Start each combat with this Card in your hand."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.selected_card = None

    def on_obtain(self):
        """Choose a Power card when this relic is obtained."""
        from engine.game_state import game_state
        add_actions([BottledCardInputRequestAction(self, CardType.POWER)])
        return
    def on_combat_start(self, player, entities):
        """Add selected card to hand at start of combat."""
        if self.selected_card:
            # Add a copy of selected card to hand
            from actions.card import AddCardAction
            from engine.game_state import game_state
            add_actions([AddCardAction(card=self.selected_card, dest_pile='hand', position=PilePosType.TOP)])
            return
        return
@register("relic")
class DarkstonePeriapt(Relic):
    """Whenever you obtain a Curse, increase your Max HP by 6."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def on_card_added(self, card, dest_pile: str = "deck"):
        """Gain max HP when obtaining a Curse."""
        if dest_pile not in ("deck"):
            return
        if getattr(card, "card_type", None) == CardType.CURSE:
            from engine.game_state import game_state
            add_actions([ModifyMaxHpAction(amount=6)])
            return
        return
@register("relic")
class EternalFeather(Relic):
    """For every 5 Cards in your deck, heal 3 HP whenever you enter a Rest Site."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    # This hooks into rest events

@register("relic")
class FrozenEgg(Relic):
    """Whenever you add a Power to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def should_upgrade_added_card(self, card, dest_pile: str = "deck") -> bool:
        """Upgrade added Power cards."""
        return (
            dest_pile in ("deck")
            and getattr(card, "card_type", None) == CardType.POWER
        )


@register("relic")
class GremlinHorn(Relic):
    """Whenever an enemy dies, gain 1 Energy and draw 1 Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_damage_dealt(self, damage, target, player, entities):
        """When an enemy dies, gain energy and draw card"""
        if target.is_dead():
            from engine.game_state import game_state
            add_actions(
            [
                GainEnergyAction(energy=1),
                DrawCardsAction(count=1)
            ]
            )
            return
        return
@register("relic")
class InkBottle(Relic):
    """Whenever you play 10 cards, draw 1 Card."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.cards_played = 0
    
    def on_card_play(self, card, player, targets):
        """Track cards played"""
        self.cards_played += 1
        if self.cards_played >= 10:
            self.cards_played = 0
            from engine.game_state import game_state
            add_actions([DrawCardsAction(count=1)])
            return
        return
@register("relic")
class Kunai(Relic):
    """Every time you play 3 Attacks in a single turn, gain 1 Dexterity."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_player_turn_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return
    def on_card_play(self, card, player, targets):
        """Track attacks played and gain Dexterity on 3rd attack"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn == 3:
                from engine.game_state import game_state
                add_actions([ApplyPowerAction(power="Dexterity", target=player, amount=1)])
                return
        return
@register("relic")
class LetterOpener(Relic):
    """Every time you play 3 Skills in a single turn, deal 5 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.skills_played_this_turn = 0
    
    def on_player_turn_start(self, player, entities):
        """Reset skill counter at start of each turn"""
        self.skills_played_this_turn = 0
        return
    def on_card_play(self, card, player, targets):
        """Track skills played and deal damage on 3rd skill"""
        if card.card_type == CardType.SKILL:
            self.skills_played_this_turn += 1
            if self.skills_played_this_turn == 3:
                from engine.game_state import game_state
                current_combat = getattr(game_state, "current_combat", None)
                enemies = getattr(current_combat, "enemies", []) if current_combat is not None else []
                actions = [
                    DealDamageAction(damage=5, target=enemy)
                    for enemy in enemies
                    if getattr(enemy, "hp", 0) > 0
                ]
                add_actions(actions)
                return
        return
@register("relic")
class Matryoshka(Relic):
    """The next 2 Chests you open contain 2 Relics."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.chests_to_spawn = 2

    def on_chest_open(self, chest_type: str | None = None):
        """Grant an extra relic from next two non-boss chests."""
        if chest_type == "boss" or self.chests_to_spawn <= 0:
            return
        from actions.reward import AddRandomRelicAction
        from engine.game_state import game_state
        import random

        self.chests_to_spawn -= 1
        if chest_type == "small":
            rarity = (
                RarityType.COMMON
                if random.random() < 0.75
                else RarityType.UNCOMMON
            )
        elif chest_type == "medium":
            rarity_roll = random.random()
            if rarity_roll < 0.35:
                rarity = RarityType.COMMON
            elif rarity_roll < 0.85:
                rarity = RarityType.UNCOMMON
            else:
                rarity = RarityType.RARE
        elif chest_type == "large":
            rarity = (
                RarityType.UNCOMMON
                if random.random() < 0.75
                else RarityType.RARE
            )
        else:
            rarity = RarityType.UNCOMMON

        character = (
            game_state.player.namespace
            if game_state and game_state.player
            else None
        )
        from engine.game_state import game_state
        add_actions(
        [
            AddRandomRelicAction(
                rarities=[rarity],
                characters=[character] if character else None,
            )
        ]
        )
        return


@register("relic")
class MeatOnBone(Relic):
    """If your HP is at or below 50% at end of combat, heal 12 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_combat_end(self, player, entities):
        """Heal if HP at or below 50% at combat end"""
        if player and player.hp <= (player.max_hp / 2):
            from engine.game_state import game_state
            add_actions([HealAction(amount=12)])
            return
        return
@register("relic")
class MercuryHourglass(Relic):
    """At the start of your turn, deal 3 damage to ALL enemies."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_player_turn_start(self, player, entities):
        """Deal 3 damage to all enemies at turn start"""
        actions = []
        for enemy in entities:
            actions.append(DealDamageAction(damage=3, target=enemy))
        from engine.game_state import game_state
        add_actions(actions)
        return
@register("relic")
class MoltenEgg(Relic):
    """Whenever you add an Attack to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def should_upgrade_added_card(self, card, dest_pile: str = "deck") -> bool:
        """Upgrade added Attack cards."""
        return (
            dest_pile in ("deck")
            and getattr(card, "card_type", None) == CardType.ATTACK
        )


@register("relic")
class MummifiedHand(Relic):
    """Whenever you play a Power, a random card in your hand costs 0 Energy for turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_card_play(self, card, player, targets):
        """Make random card in hand cost 0 for turn"""
        if card.card_type == CardType.POWER:
            from engine.game_state import game_state
            hand = game_state.player.card_manager.get_pile('hand')
            if hand:
                import random
                target_card = random.choice(hand)
                target_card.temp_cost = 0
        return
@register("relic")
class OrnamentalFan(Relic):
    """Every time you play 3 Attacks in a single turn, gain 4 Block."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_player_turn_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return
    def on_card_play(self, card, player, targets):
        """Track attacks played and gain Block on 3rd attack"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn == 3:
                from engine.game_state import game_state
                add_actions([GainBlockAction(block=4, target=player)])
                return
        return
@register("relic")
class Pantograph(Relic):
    """At the start of Boss combats, heal 25 HP."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_combat_start(self, player, entities):
        """Heal 25 HP at start of boss combat"""
        from engine.game_state import game_state
        from utils.types import CombatType
        
        if game_state.current_combat is not None:
            if game_state.current_combat.combat_type != CombatType.NORMAL:
                from engine.game_state import game_state
                add_actions([ApplyPowerAction(power="Regeneration", target=player, amount=25, duration=1)])
                return
        return
@register("relic")
class PaperPhrog(Relic):
    """Enemies with Vulnerable take 75% more damage rather than 50%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.damage_phase = DamagePhase.MULTIPLICATIVE  # Vulnerable multiplier adjustment

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Vulnerable increases damage by 75% instead of 50%."""
        if target and hasattr(target, "powers"):
            for power in target.powers:
                if getattr(power, "name", "") == "Vulnerable":
                    # Vulnerable multiplier (x1.5) is applied later in pipeline.
                    # Pre-scale by 7/6 so total becomes x1.75.
                    return int(base_damage * 7 / 6)
        return base_damage


@register("relic")
class Pear(Relic):
    """Raise your Max HP by 10."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
    
    def on_obtain(self):
        from engine.game_state import game_state
        add_actions([ModifyMaxHpAction(amount=10)])
        return
@register("relic")
class QuestionCard(Relic):
    """On future Card Reward screens you have 1 additional Card to choose from."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def modify_card_reward_count(self, base_count: int, encounter_type: str = "normal") -> int:
        """Increase card reward options by 1."""
        return base_count + 1


@register("relic")
class SelfFormingClay(Relic):
    """Whenever you lose HP in combat, gain 3 Block next turn."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.block_gain_next_turn = 0
    
    def on_damage_taken(self, damage, source, player, entities):
        """Track HP loss to gain Block next turn"""
        if damage > 0:
            self.block_gain_next_turn = 3
        return
    def on_player_turn_start(self, player, entities):
        """Gain Block if HP was lost last turn"""
        if self.block_gain_next_turn > 0:
            block = self.block_gain_next_turn
            self.block_gain_next_turn = 0
            from engine.game_state import game_state
            add_actions([GainBlockAction(block=block, target=player)])
            return
        return
@register("relic")
class Shuriken(Relic):
    """Every time you play 3 Attacks in a single turn, gain 1 Strength."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.attacks_played_this_turn = 0
    
    def on_player_turn_start(self, player, entities):
        """Reset attack counter at start of each turn"""
        self.attacks_played_this_turn = 0
        return
    def on_card_play(self, card, player, targets):
        """Track attacks played and gain Strength on 3rd attack"""
        if card.card_type == CardType.ATTACK:
            self.attacks_played_this_turn += 1
            if self.attacks_played_this_turn == 3:
                from engine.game_state import game_state
                add_actions([ApplyPowerAction(power="Strength", target=player, amount=1)])
                return
        return
@register("relic")
class SingingBowl(Relic):
    """When adding Cards to your deck, you may gain +2 Max HP instead."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def can_choose_max_hp_instead_of_card(self) -> bool:
        """Enable +2 max HP option on card reward screens."""
        return True


@register("relic")
class StrikeDummy(Relic):
    """Cards containing "Strike" deal 3 additional damage."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.damage_phase = DamagePhase.ADDITIVE  # +3 damage for Strike cards

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Add 3 damage to Strike cards."""
        if card and getattr(card, "card_type", None) == CardType.ATTACK:
            card_id = getattr(card, "idstr", "").lower()
            card_name = str(getattr(card, "display_name", "")).lower()
            if "strike" in card_id or "strike" in card_name:
                return base_damage + 3
        return base_damage


@register("relic")
class Sundial(Relic):
    """Every 3 times you shuffle your Drawpile, gain 2 Energy."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON
        self.shuffle_count = 0
    
    def on_shuffle(self):
        """Gain 2 energy every 3 shuffles"""
        self.shuffle_count += 1
        if self.shuffle_count % 3 == 0:
            from actions.combat import GainEnergyAction
            from engine.game_state import game_state
            add_actions([GainEnergyAction(energy=2)])
            return
        return
@register("relic")
class TheCourier(Relic):
    """The merchant no longer runs out of Cards, Relics, or Potions and his prices are reduced by 20%."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def should_restock_shop_item(self, item_type: str, item=None) -> bool:
        """Restock purchased non-shop-relic items."""
        if item_type == "remove":
            return False
        if item_type != "relic":
            return True
        return getattr(item, "rarity", None) != RarityType.SHOP


@register("relic")
class ToxicEgg(Relic):
    """Whenever you add a Skill to your deck, it is Upgraded."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def should_upgrade_added_card(self, card, dest_pile: str = "deck") -> bool:
        """Upgrade added Skill cards."""
        return (
            dest_pile in ("deck")
            and getattr(card, "card_type", None) == CardType.SKILL
        )


@register("relic")
class WhiteBeastStatue(Relic):
    """Potions always drop after combat."""
    
    def __init__(self):
        super().__init__()
        self.rarity = RarityType.UNCOMMON

    def forces_potion_drop(self) -> bool:
        """Always drop potion rewards after combat."""
        return True

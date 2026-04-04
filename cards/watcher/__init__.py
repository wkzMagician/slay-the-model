"""Watcher card package."""

from __future__ import annotations

from typing import List

from actions.card import AddCardAction, DrawCardsAction
from actions.card_choice import ChooseAddRandomCardAction, ChooseCardLambdaAction, MoveCardAction, SetCostUntilEndOfTurnAction
from actions.card_lifecycle import ExhaustCardAction
from actions.combat import EndTurnAction, GainBlockAction, GainEnergyAction
from actions.combat_cards import AttackAction, PlayCardAction
from actions.combat_damage import LoseHPAction
from actions.combat_status import ApplyPowerAction
from actions.display import InputRequestAction
from actions.watcher import ChangeStanceAction, GainMantraAction, ReturnCardToHandAction, ScryAction, SkipEnemyTurnAction, TriggerMarkAction
from cards.base import COST_UNPLAYABLE, COST_X, Card, RawLocalStr
from engine.messages import ScryMessage, StanceChangedMessage
from engine.runtime_api import add_action, add_actions
from engine.subscriptions import MessagePriority, subscribe
from powers.definitions.dexterity import DexterityPower
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from powers.definitions.plated_armor import PlatedArmorPower
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from powers.definitions.watcher import (
    BattleHymnPower,
    BlasphemerPower,
    CollectPower,
    DevotionPower,
    EstablishmentPower,
    FastingPower,
    ForesightPower,
    LikeWaterPower,
    MarkPower,
    MasterRealityPower,
    MentalFortressPower,
    NirvanaPower,
    OmegaPower,
    RushdownPower,
    TalkToTheHandPower,
    WaveOfTheHandPower,
    WreathOfFlamePower,
)
from utils.dynamic_values import resolve_potential_damage
from utils.option import Option
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType
from watcher_support import StaticTextMixin


def _player():
    from engine.game_state import game_state

    return game_state.player


def _combat():
    from engine.game_state import game_state

    return game_state.current_combat


def _alive_enemies():
    combat = _combat()
    return [enemy for enemy in (combat.enemies if combat else []) if not enemy.is_dead()]


def _last_played_card():
    player = _player()
    if player is None:
        return None
    discard = player.card_manager.get_pile("discard_pile")
    return discard[-1] if discard else None


class WatcherCard(StaticTextMixin, Card):
    text_name = ""
    text_description = ""


class WatcherAttack(WatcherCard):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT


class WatcherSkill(WatcherCard):
    card_type = CardType.SKILL
    target_type = TargetType.SELF


class WatcherPowerCard(WatcherCard):
    card_type = CardType.POWER
    target_type = TargetType.SELF


@register("card")
class Miracle(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_energy_gain = 1
    upgrade_energy_gain = 2
    base_exhaust = True
    text_name = "Miracle"
    text_description = "Gain {energy_gain} Energy. Exhaust."


@register("card")
class Smite(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    base_retain = True
    base_exhaust = True
    text_name = "Smite"
    text_description = "Retain. Deal {damage} damage. Exhaust."


@register("card")
class Safety(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_block = 12
    upgrade_block = 16
    base_retain = True
    base_exhaust = True
    text_name = "Safety"
    text_description = "Retain. Gain {block} Block. Exhaust."


@register("card")
class Insight(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_draw = 2
    upgrade_draw = 3
    base_retain = True
    base_exhaust = True
    text_name = "Insight"
    text_description = "Retain. Draw {draw} cards. Exhaust."


@register("card")
class ThroughViolence(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 0
    base_damage = 20
    upgrade_damage = 30
    base_retain = True
    base_exhaust = True
    text_name = "Through Violence"
    text_description = "Retain. Deal {damage} damage. Exhaust."


@register("card")
class Expunger(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 9
    base_exhaust = True
    text_name = "Expunger"
    text_description = "Deal {damage} damage X times. Exhaust."

    def __init__(self, hits: int = 1, **kwargs):
        self.hits = max(1, hits)
        super().__init__(**kwargs)

    def get_combat_description(self, target=None):
        player = _player()
        damage = self.damage
        if player is not None and target is not None:
            damage = resolve_potential_damage(self.damage, player, target, card=self)
        return RawLocalStr(f"Deal {damage} damage {self.hits} times. Exhaust.")

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(self.hits):
            add_action(AttackAction(self.damage, target=target, source=_player(), damage_type="attack", card=self))


@register("card")
class Beta(WatcherSkill):
    rarity = RarityType.SPECIAL
    base_cost = 2
    base_exhaust = True
    text_name = "Beta"
    text_description = "Shuffle an Omega into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        add_action(AddCardAction(Omega(), dest_pile="draw_pile"))


@register("card")
class Omega(WatcherPowerCard):
    rarity = RarityType.SPECIAL
    base_cost = 3
    base_exhaust = True
    text_name = "Omega"
    text_description = "At the end of your turn, deal 50 damage to ALL enemies."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(OmegaPower(amount=50, owner=_player()), _player()))


@register("card")
class Strike(WatcherAttack):
    rarity = RarityType.STARTER
    base_cost = 1
    base_damage = 6
    upgrade_damage = 9
    text_name = "Strike"
    text_description = "Deal {damage} damage."


@register("card")
class Defend(WatcherSkill):
    rarity = RarityType.STARTER
    base_cost = 1
    base_block = 5
    upgrade_block = 8
    text_name = "Defend"
    text_description = "Gain {block} Block."


@register("card")
class Eruption(WatcherAttack):
    rarity = RarityType.STARTER
    base_cost = 2
    upgrade_cost = 1
    base_damage = 9
    upgrade_damage = 12
    text_name = "Eruption"
    text_description = "Deal {damage} damage. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))


@register("card")
class Vigilance(WatcherSkill):
    rarity = RarityType.STARTER
    base_cost = 2
    base_block = 8
    upgrade_block = 12
    text_name = "Vigilance"
    text_description = "Gain {block} Block. Enter Calm."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.CALM))


@register("card")
class BowlingBash(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 10
    text_name = "Bowling Bash"
    text_description = "Deal {damage} damage for each enemy in combat."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(max(1, len(_alive_enemies()))):
            add_action(AttackAction(self.damage, target=target, source=_player(), damage_type="attack", card=self))


@register("card")
class Consecrate(WatcherAttack):
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 0
    base_damage = 5
    upgrade_damage = 8
    text_name = "Consecrate"
    text_description = "Deal {damage} damage to ALL enemies."


@register("card")
class Crescendo(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    upgrade_cost = 0
    base_retain = True
    base_exhaust = True
    text_name = "Crescendo"
    text_description = "Retain. Enter Wrath. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.WRATH))


@register("card")
class CrushJoints(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"vuln": 1}
    upgrade_magic = {"vuln": 2}
    text_name = "Crush Joints"
    text_description = "Deal {damage} damage. If the previous card played this turn was a Skill, apply {magic.vuln} Vulnerable."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        previous = _last_played_card()
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.SKILL:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))


@register("card")
class CutThroughFate(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 9
    base_magic = {"scry": 2}
    upgrade_magic = {"scry": 3}
    base_draw = 1
    text_name = "Cut Through Fate"
    text_description = "Deal {damage} damage. Scry {magic.scry}. Draw {draw} card."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_actions([ScryAction(self.get_magic_value("scry")), DrawCardsAction(self.draw)])


@register("card")
class EmptyBody(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 7
    upgrade_block = 10
    text_name = "Empty Body"
    text_description = "Gain {block} Block. Exit your stance."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.NEUTRAL))


@register("card")
class EmptyFist(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 9
    upgrade_damage = 14
    text_name = "Empty Fist"
    text_description = "Deal {damage} damage. Exit your stance."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.NEUTRAL))


@register("card")
class Evaluate(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 10
    text_name = "Evaluate"
    text_description = "Gain {block} Block. Shuffle an Insight into your draw pile."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(AddCardAction(Insight(), dest_pile="draw_pile"))


@register("card")
class FlurryOfBlows(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Flurry of Blows"
    text_description = "Deal {damage} damage. Whenever you change stances, return this from your discard pile to your hand."

    @subscribe(StanceChangedMessage, priority=MessagePriority.CARD)
    def on_stance_changed(self, previous_status, new_status):
        add_action(ReturnCardToHandAction(self))


@register("card")
class FlyingSleeves(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 4
    upgrade_damage = 6
    base_attack_times = 2
    base_retain = True
    text_name = "Flying Sleeves"
    text_description = "Retain. Deal {damage} damage {attack_times} times."


@register("card")
class FollowUp(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 11
    text_name = "Follow-Up"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, gain 1 Energy."

    def on_play(self, targets: List = []):
        previous = _last_played_card()
        super().on_play(targets)
        if previous is not None and getattr(previous, "card_type", None) == CardType.ATTACK:
            add_action(GainEnergyAction(1))


@register("card")
class Halt(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 3
    upgrade_block = 4
    base_magic = {"wrath_block": 9}
    upgrade_magic = {"wrath_block": 14}
    text_name = "Halt"
    text_description = "Gain {block} Block. If you are in Wrath, gain {magic.wrath_block} more."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if _player().status_manager.status == StatusType.WRATH:
            add_action(GainBlockAction(self.get_magic_value("wrath_block"), target=_player()))


@register("card")
class JustLucky(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 3
    upgrade_damage = 4
    base_block = 2
    upgrade_block = 3
    text_name = "Just Lucky"
    text_description = "Deal {damage} damage. Scry 1. Gain {block} Block."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(1))


@register("card")
class PressurePoints(WatcherSkill):
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"mark": 8}
    upgrade_magic = {"mark": 11}
    text_name = "Pressure Points"
    text_description = "Apply {magic.mark} Mark. ALL enemies lose HP equal to their Mark."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        add_action(ApplyPowerAction(MarkPower(amount=self.get_magic_value("mark"), owner=target), target))
        for enemy in _alive_enemies():
            add_action(TriggerMarkAction(enemy))


@register("card")
class Prostrate(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 0
    base_block = 4
    upgrade_block = 6
    base_exhaust = True
    text_name = "Prostrate"
    text_description = "Gain {block} Block. Gain 2 Mantra. Exhaust."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(2))


@register("card")
class Protect(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 2
    upgrade_cost = 1
    base_block = 12
    upgrade_block = 16
    base_retain = True
    text_name = "Protect"
    text_description = "Retain. Gain {block} Block."


@register("card")
class SashWhip(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Sash Whip"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, apply {magic.weak} Weak."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        previous = _last_played_card()
        super().on_play(targets)
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.ATTACK:
            return
        amount = self.get_magic_value("weak")
        add_action(ApplyPowerAction(WeakPower(amount=amount, duration=amount, owner=target), target))


@register("card")
class ThirdEye(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    base_block = 7
    upgrade_block = 9
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 5}
    text_name = "Third Eye"
    text_description = "Gain {block} Block. Scry {magic.scry}."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ScryAction(self.get_magic_value("scry")))


@register("card")
class Tranquility(WatcherSkill):
    rarity = RarityType.COMMON
    base_cost = 1
    upgrade_cost = 0
    base_retain = True
    base_exhaust = True
    text_name = "Tranquility"
    text_description = "Retain. Enter Calm. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.CALM))


@register("card")
class BattleHymn(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    text_name = "Battle Hymn"
    text_description = "At the start of your turn, add a Smite into your hand."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(BattleHymnPower(owner=_player()), _player()))


@register("card")
class CarveReality(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 6
    upgrade_damage = 10
    text_name = "Carve Reality"
    text_description = "Deal {damage} damage. Add a Smite into your hand."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(AddCardAction(Smite(), dest_pile="hand"))


@register("card")
class Collect(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = COST_X
    base_exhaust = True
    text_name = "Collect"
    text_description = "Put Miracle+ into your hand at the start of your next X turns. Exhaust."

    def on_play(self, targets: List = []):
        duration = self.get_effective_x() + (1 if self.upgrade_level > 0 else 0)
        add_action(ApplyPowerAction(CollectPower(duration=duration, owner=_player()), _player()))


@register("card")
class Conclude(WatcherAttack):
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_ALL
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Conclude"
    text_description = "Deal {damage} damage to ALL enemies. End your turn."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(EndTurnAction())


@register("card")
class DeceiveReality(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 7
    text_name = "Deceive Reality"
    text_description = "Gain {block} Block. Add a Safety into your hand."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(AddCardAction(Safety(), dest_pile="hand"))


@register("card")
class EmptyMind(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 2
    upgrade_draw = 3
    text_name = "Empty Mind"
    text_description = "Exit your stance. Draw {draw} cards."

    def on_play(self, targets: List = []):
        add_actions([ChangeStanceAction(StatusType.NEUTRAL), DrawCardsAction(self.draw)])


@register("card")
class Fasting(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_magic = {"stat": 3}
    upgrade_magic = {"stat": 4}
    text_name = "Fasting"
    text_description = "Gain {magic.stat} Strength and Dexterity. Gain 1 less Energy at the start of each turn."

    def on_play(self, targets: List = []):
        amount = self.get_magic_value("stat")
        player = _player()
        add_actions(
            [
                ApplyPowerAction(StrengthPower(amount=amount, owner=player), player),
                ApplyPowerAction(DexterityPower(amount=amount, owner=player), player),
                ApplyPowerAction(FastingPower(owner=player), player),
            ]
        )


@register("card")
class FearNoEvil(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 11
    text_name = "Fear No Evil"
    text_description = "Deal {damage} damage. If the enemy intends to attack, gain 2 Energy."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None and getattr(target, "current_intention", None) is not None:
            if "attack" in getattr(target.current_intention, "name", "").lower():
                add_action(GainEnergyAction(2))


@register("card")
class ForeignInfluence(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_exhaust = True
    text_name = "Foreign Influence"
    text_description = "Choose 1 of 3 attacks from any color to add to your hand. It costs 0 this turn. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChooseAddRandomCardAction(total=3, card_type=CardType.ATTACK, cost_until_end_of_turn=0))


@register("card")
class Foresight(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"scry": 3}
    upgrade_magic = {"scry": 4}
    text_name = "Foresight"
    text_description = "At the start of your turn, Scry {magic.scry}."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(ForesightPower(amount=self.get_magic_value("scry"), owner=_player()), _player()))


@register("card")
class Indignation(WatcherSkill):
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"vuln": 3}
    upgrade_magic = {"vuln": 5}
    text_name = "Indignation"
    text_description = "Apply {magic.vuln} Vulnerable."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))


@register("card")
class InnerPeace(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_draw = 3
    upgrade_draw = 4
    text_name = "Inner Peace"
    text_description = "Enter Calm. If you are already in Calm, draw {draw} cards."

    def on_play(self, targets: List = []):
        was_calm = _player().status_manager.status == StatusType.CALM
        add_action(ChangeStanceAction(StatusType.CALM))
        if was_calm:
            add_action(DrawCardsAction(self.draw))


@register("card")
class LikeWater(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 5}
    upgrade_magic = {"block": 7}
    text_name = "Like Water"
    text_description = "At the end of your turn, if you are in Calm, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(LikeWaterPower(amount=self.get_magic_value("block"), owner=_player()), _player()))


@register("card")
class Meditate(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"pick": 1}
    upgrade_magic = {"pick": 2}
    base_exhaust = True
    text_name = "Meditate"
    text_description = "Put up to {magic.pick} cards from your discard pile into your hand. Enter Calm. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.CALM))
        add_action(
            ChooseCardLambdaAction(
                pile="discard_pile",
                amount=self.get_magic_value("pick"),
                must_select=False,
                action_builder=lambda card: MoveCardAction(card=card, src_pile="discard_pile", dst_pile="hand"),
            )
        )


@register("card")
class MentalFortress(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 4}
    upgrade_magic = {"block": 6}
    text_name = "Mental Fortress"
    text_description = "Whenever you change stances, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MentalFortressPower(amount=self.get_magic_value("block"), owner=_player()), _player()))


@register("card")
class Nirvana(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"block": 3}
    upgrade_magic = {"block": 4}
    text_name = "Nirvana"
    text_description = "Whenever you Scry, gain {magic.block} Block."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(NirvanaPower(amount=self.get_magic_value("block"), owner=_player()), _player()))


@register("card")
class Perseverance(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 5
    upgrade_block = 7
    base_magic = {"retain_gain": 2}
    upgrade_magic = {"retain_gain": 3}
    base_retain = True
    text_name = "Perseverance"
    text_description = "Retain. Gain {block} Block. When retained, this gains {magic.retain_gain} Block."

    def on_player_turn_end(self):
        if self in _player().card_manager.get_pile("hand"):
            self._block += self.get_magic_value("retain_gain")


@register("card")
class Pray(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 4
    upgrade_block = 5
    text_name = "Pray"
    text_description = "Gain {block} Block. Gain 3 Mantra."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(GainMantraAction(3))


@register("card")
class ReachHeaven(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 10
    upgrade_damage = 15
    text_name = "Reach Heaven"
    text_description = "Deal {damage} damage. Shuffle a Through Violence into your draw pile."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(AddCardAction(ThroughViolence(), dest_pile="draw_pile"))


@register("card")
class Rushdown(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"draw": 2}
    text_name = "Rushdown"
    text_description = "Whenever you enter Wrath, draw {magic.draw} cards."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(RushdownPower(amount=self.get_magic_value("draw"), owner=_player()), _player()))


@register("card")
class Sanctity(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_block = 6
    upgrade_block = 9
    text_name = "Sanctity"
    text_description = "Gain {block} Block. If you are in Calm, draw 2 cards."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        if _player().status_manager.status == StatusType.CALM:
            add_action(DrawCardsAction(2))


@register("card")
class SandsOfTime(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 4
    base_damage = 20
    upgrade_damage = 26
    base_retain = True
    text_name = "Sands of Time"
    text_description = "Retain. Deal {damage} damage. Retaining this card reduces its cost by 1."

    def on_player_turn_end(self):
        if self in _player().card_manager.get_pile("hand") and self._cost > 0:
            self._cost -= 1


@register("card")
class SignatureMove(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 30
    upgrade_damage = 40
    text_name = "Signature Move"
    text_description = "Can only be played if this is the only Attack in your hand. Deal {damage} damage."

    def can_play(self, ignore_energy=False):
        can_play, reason = super().can_play(ignore_energy)
        if not can_play:
            return can_play, reason
        hand = _player().card_manager.get_pile("hand")
        if any(card is not self and getattr(card, "card_type", None) == CardType.ATTACK for card in hand):
            return False, "Signature Move requires no other attacks in hand."
        return True, None


@register("card")
class SimmeringFury(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"next_draw": 2}
    upgrade_magic = {"next_draw": 3}
    text_name = "Simmering Fury"
    text_description = "Enter Wrath. Next turn, draw {magic.next_draw} cards."

    def on_play(self, targets: List = []):
        player = _player()
        add_actions(
            [
                ChangeStanceAction(StatusType.WRATH),
                ApplyPowerAction(DrawCardNextTurnPower(amount=self.get_magic_value("next_draw"), duration=1, owner=player), player),
            ]
        )


@register("card")
class Study(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"amount": 2}
    upgrade_magic = {"amount": 3}
    text_name = "Study"
    text_description = "At the end of your turn, shuffle {magic.amount} Insight into your draw pile."

    def on_play(self, targets: List = []):
        from powers.definitions.watcher import StudyPower

        add_action(ApplyPowerAction(StudyPower(amount=self.get_magic_value("amount"), owner=_player()), _player()))


@register("card")
class Swivel(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_block = 8
    upgrade_block = 11
    text_name = "Swivel"
    text_description = "Gain {block} Block. Your next Attack this turn costs 0."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        for card in list(_player().card_manager.get_pile("hand")):
            if getattr(card, "card_type", None) == CardType.ATTACK:
                add_action(SetCostUntilEndOfTurnAction(card, 0))


@register("card")
class TalkToTheHand(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 5
    upgrade_damage = 8
    base_magic = {"block": 2}
    text_name = "Talk to the Hand"
    text_description = "Deal {damage} damage. Apply a debuff that gives you {magic.block} Block whenever you attack that enemy."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            add_action(ApplyPowerAction(TalkToTheHandPower(amount=self.get_magic_value("block"), owner=target), target))


@register("card")
class Tantrum(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_damage = 3
    upgrade_damage = 4
    base_attack_times = 3
    text_name = "Tantrum"
    text_description = "Deal {damage} damage {attack_times} times. Enter Wrath."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(ChangeStanceAction(StatusType.WRATH))


@register("card")
class Wallop(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 9
    upgrade_damage = 12
    text_name = "Wallop"
    text_description = "Deal {damage} damage. Gain Block equal to damage dealt."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            predicted = resolve_potential_damage(self.damage, _player(), target, card=self)
            add_action(GainBlockAction(predicted, target=_player()))


@register("card")
class WaveOfTheHand(WatcherPowerCard):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Wave of the Hand"
    text_description = "Whenever you gain Block this turn, apply {magic.weak} Weak to ALL enemies."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(WaveOfTheHandPower(amount=self.get_magic_value("weak"), duration=1, owner=_player()), _player()))


@register("card")
class Weave(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Weave"
    text_description = "Deal {damage} damage. Whenever you Scry, return this from your discard pile to your hand."

    @subscribe(ScryMessage, priority=MessagePriority.CARD)
    def on_scry(self, count):
        add_action(ReturnCardToHandAction(self))


@register("card")
class WheelKick(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 15
    upgrade_damage = 20
    base_draw = 2
    text_name = "Wheel Kick"
    text_description = "Deal {damage} damage. Draw {draw} cards."

    def on_play(self, targets: List = []):
        super().on_play(targets)
        add_action(DrawCardsAction(self.draw))


@register("card")
class WindmillStrike(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 7
    upgrade_damage = 10
    base_retain = True
    base_magic = {"gain": 4}
    upgrade_magic = {"gain": 5}
    text_name = "Windmill Strike"
    text_description = "Retain. Deal {damage} damage. Retaining this card increases its damage by {magic.gain}."

    def on_player_turn_end(self):
        if self in _player().card_manager.get_pile("hand"):
            self._damage += self.get_magic_value("gain")


@register("card")
class Worship(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    upgrade_cost = 1
    text_name = "Worship"
    text_description = "Gain 5 Mantra."

    def on_play(self, targets: List = []):
        add_action(GainMantraAction(5))


@register("card")
class WreathOfFlame(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"bonus": 5}
    upgrade_magic = {"bonus": 8}
    text_name = "Wreath of Flame"
    text_description = "Your next Attack deals {magic.bonus} additional damage."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(WreathOfFlamePower(amount=self.get_magic_value("bonus"), owner=_player()), _player()))


@register("card")
class Alpha(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Alpha"
    text_description = "Shuffle a Beta into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        add_action(AddCardAction(Beta(), dest_pile="draw_pile"))


@register("card")
class Blasphemy(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Blasphemy"
    text_description = "Enter Divinity. Die next turn. Exhaust."

    def on_play(self, targets: List = []):
        player = _player()
        add_actions([ChangeStanceAction(StatusType.DIVINITY), ApplyPowerAction(BlasphemerPower(owner=player), player)])


@register("card")
class Brilliance(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 1
    base_damage = 12
    upgrade_damage = 16
    text_name = "Brilliance"
    text_description = "Deal {damage} damage. Deals more damage for your Mantra."

    def on_play(self, targets: List = []):
        mantra = _player().get_power("Mantra")
        if mantra is not None:
            self._damage += mantra.amount
        super().on_play(targets)
        self._damage = self.base_damage if self.upgrade_level == 0 else self.upgrade_damage


@register("card")
class ConjureBlade(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = COST_X
    base_exhaust = True
    text_name = "Conjure Blade"
    text_description = "Shuffle an Expunger into your draw pile. Exhaust."

    def on_play(self, targets: List = []):
        hits = self.get_effective_x() + (1 if self.upgrade_level > 0 else 0)
        add_action(AddCardAction(Expunger(hits=max(1, hits)), dest_pile="draw_pile"))


@register("card")
class DeusExMachina(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = COST_UNPLAYABLE
    base_exhaust = True
    base_magic = {"count": 2}
    upgrade_magic = {"count": 3}
    text_name = "Deus Ex Machina"
    text_description = "Unplayable. When drawn, add {magic.count} Miracles to your hand. Exhaust."

    def on_draw(self):
        for _ in range(self.get_magic_value("count")):
            add_action(AddCardAction(Miracle(), dest_pile="hand"))
        add_action(ExhaustCardAction(self, source_pile="hand"))


@register("card")
class DevaForm(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 3
    text_name = "Deva Form"
    text_description = "At the start of your turn, gain Energy and increase this effect."

    def on_play(self, targets: List = []):
        from powers.definitions.watcher import DevaPower

        add_action(ApplyPowerAction(DevaPower(duration=1, owner=_player()), _player()))


@register("card")
class Devotion(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    base_magic = {"mantra": 2}
    upgrade_magic = {"mantra": 3}
    text_name = "Devotion"
    text_description = "At the start of your turn, gain {magic.mantra} Mantra."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(DevotionPower(amount=self.get_magic_value("mantra"), owner=_player()), _player()))


@register("card")
class Establishment(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Establishment"
    text_description = "At the end of your turn, reduce the cost of retained cards by 1."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(EstablishmentPower(owner=_player()), _player()))


@register("card")
class Judgment(WatcherSkill):
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"threshold": 30}
    upgrade_magic = {"threshold": 40}
    text_name = "Judgment"
    text_description = "If the enemy has {magic.threshold} HP or less, it dies."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is not None and target.hp <= self.get_magic_value("threshold"):
            add_action(LoseHPAction(amount=target.hp, target=target, source=self, card=self))


@register("card")
class LessonLearned(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 2
    base_damage = 10
    upgrade_damage = 13
    text_name = "Lesson Learned"
    text_description = "Deal {damage} damage. If Fatal, upgrade a card in your deck."

    def on_fatal(self, damage, target=None, card=None, damage_type: str = "direct"):
        if card is not self:
            return
        for candidate in _player().card_manager.get_pile("deck"):
            if candidate.can_upgrade():
                candidate.upgrade()
                break


@register("card")
class MasterReality(WatcherPowerCard):
    rarity = RarityType.RARE
    base_cost = 1
    text_name = "Master Reality"
    text_description = "Whenever a card is created during combat, upgrade it."

    def on_play(self, targets: List = []):
        add_action(ApplyPowerAction(MasterRealityPower(owner=_player()), _player()))


@register("card")
class Omniscience(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 4
    upgrade_cost = 3
    base_exhaust = True
    text_name = "Omniscience"
    text_description = "Choose a card in your hand. Play it twice. Exhaust."

    def on_play(self, targets: List = []):
        options = []
        for card in list(_player().card_manager.get_pile("hand")):
            if card is self:
                continue
            options.append(
                Option(
                    name=card.info(),
                    actions=[PlayCardAction(card, ignore_energy=True), PlayCardAction(card, ignore_energy=True)],
                )
            )
        if options:
            add_action(InputRequestAction(title=RawLocalStr("Choose a card to play twice"), options=options))


@register("card")
class Ragnarok(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 3
    base_damage = 5
    upgrade_damage = 6
    base_attack_times = 5
    upgrade_attack_times = 6
    text_name = "Ragnarok"
    text_description = "Deal {damage} damage to a random enemy {attack_times} times."

    def on_play(self, targets: List = []):
        import random

        enemies = _alive_enemies()
        for _ in range(self.attack_times):
            if enemies:
                add_action(AttackAction(self.damage, target=random.choice(enemies), source=_player(), damage_type="attack", card=self))


@register("card")
class Scrawl(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Scrawl"
    text_description = "Draw cards until your hand is full. Exhaust."

    def on_play(self, targets: List = []):
        player = _player()
        draw_needed = max(0, player.card_manager.HAND_LIMIT - len(player.card_manager.get_pile("hand")))
        if draw_needed:
            add_action(DrawCardsAction(draw_needed))


@register("card")
class SpiritShield(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 2
    base_magic = {"per_card": 3}
    upgrade_magic = {"per_card": 4}
    text_name = "Spirit Shield"
    text_description = "Gain Block equal to {magic.per_card} for each card in your hand."

    def on_play(self, targets: List = []):
        amount = len(_player().card_manager.get_pile("hand")) * self.get_magic_value("per_card")
        add_action(GainBlockAction(amount, target=_player()))


@register("card")
class Vault(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 3
    upgrade_cost = 2
    base_exhaust = True
    text_name = "Vault"
    text_description = "End your turn. Take another turn after this one."

    def on_play(self, targets: List = []):
        add_actions([SkipEnemyTurnAction(), EndTurnAction()])


@register("card")
class Wish(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 3
    base_exhaust = True
    text_name = "Wish"
    text_description = "Choose one: Gain Gold, Strength, or Plated Armor. Exhaust."

    def on_play(self, targets: List = []):
        from actions.base import LambdaAction

        player = _player()
        options = [
            Option(name=RawLocalStr("Gain Gold"), actions=[LambdaAction(lambda: setattr(player, "gold", player.gold + (30 if self.upgrade_level > 0 else 25)))]),
            Option(name=RawLocalStr("Gain Strength"), actions=[ApplyPowerAction(StrengthPower(amount=4 if self.upgrade_level > 0 else 3, owner=player), player)]),
            Option(name=RawLocalStr("Gain Plated Armor"), actions=[ApplyPowerAction(PlatedArmorPower(amount=8 if self.upgrade_level > 0 else 6, owner=player), player)]),
        ]
        add_action(InputRequestAction(title=RawLocalStr("Choose a wish"), options=options))


__all__ = [name for name in globals() if not name.startswith("_")]

from __future__ import annotations

from actions.card import AddCardAction, DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction
from actions.combat_damage import DealDamageAction, LoseHPAction
from actions.combat_status import ApplyPowerAction, RemovePowerAction
from engine.messages import CardAddedToPileMessage, ScryMessage, StanceChangedMessage
from engine.runtime_api import add_action, add_actions
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from powers.definitions.dexterity import DexterityPower
from powers.definitions.weak import WeakPower
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import CardType, StatusType
from watcher_support import StaticTextMixin


class WatcherPower(StaticTextMixin, Power):
    text_name = ""
    text_description = ""

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.name = self.text_name or self.__class__.__name__.replace("Power", "")


@register("power")
class MantraPower(WatcherPower):
    text_name = "Mantra"
    text_description = "When this reaches 10, enter Divinity."
    stack_type = StackType.INTENSITY


@register("power")
class BattleHymnPower(WatcherPower):
    text_name = "Battle Hymn"
    text_description = "At the start of your turn, add a Smite into your hand."
    stack_type = StackType.PRESENCE

    def on_turn_start(self):
        from cards.watcher import Smite

        add_action(AddCardAction(Smite(), dest_pile="hand"))


@register("power")
class CollectPower(WatcherPower):
    text_name = "Collect"
    text_description = "At the start of your turn, add Miracle+ to your hand."
    stack_type = StackType.DURATION

    def on_turn_start(self):
        from cards.watcher import Miracle

        if self.duration == 0:
            return
        miracle = Miracle()
        miracle.upgrade()
        add_action(AddCardAction(miracle, dest_pile="hand"))
        if self.duration > 0:
            self.duration -= 1
            if self.duration == 0 and self.owner is not None:
                add_action(RemovePowerAction("Collect", self.owner))


@register("power")
class DevotionPower(WatcherPower):
    text_name = "Devotion"
    text_description = "At the start of your turn, gain {amount} Mantra."

    def on_turn_start(self):
        from actions.watcher import GainMantraAction

        add_action(GainMantraAction(self.amount))


@register("power")
class EstablishmentPower(WatcherPower):
    text_name = "Establishment"
    text_description = "At the end of your turn, reduce the cost of retained cards by 1."
    stack_type = StackType.PRESENCE

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is None:
            return
        for card in list(self.owner.card_manager.get_pile("hand")):
            if getattr(card, "retain", False) or getattr(card, "retain_this_turn", False):
                if getattr(card, "_cost", 0) >= 0:
                    card._cost = max(0, card._cost - 1)


@register("power")
class ForesightPower(WatcherPower):
    text_name = "Foresight"
    text_description = "At the start of your turn, Scry {amount}."

    def on_turn_start(self):
        from actions.watcher import ScryAction

        add_action(ScryAction(self.amount))


@register("power")
class LikeWaterPower(WatcherPower):
    text_name = "Like Water"
    text_description = "At the end of your turn, if you are in Calm, gain {amount} Block."

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is None:
            return
        if self.owner.status_manager.status == StatusType.CALM:
            add_action(GainBlockAction(self.amount, target=self.owner))


@register("power")
class MentalFortressPower(WatcherPower):
    text_name = "Mental Fortress"
    text_description = "Whenever you change stances, gain {amount} Block."
    stack_type = StackType.INTENSITY

    @subscribe(StanceChangedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_stance_changed(self, previous_status, new_status):
        if previous_status != new_status and self.owner is not None:
            add_action(GainBlockAction(self.amount, target=self.owner))


@register("power")
class NirvanaPower(WatcherPower):
    text_name = "Nirvana"
    text_description = "Whenever you Scry, gain {amount} Block."

    @subscribe(ScryMessage, priority=MessagePriority.PLAYER_POWER)
    def on_scry(self, count):
        if count > 0 and self.owner is not None:
            add_action(GainBlockAction(self.amount, target=self.owner))


@register("power")
class RushdownPower(WatcherPower):
    text_name = "Rushdown"
    text_description = "Whenever you enter Wrath, draw {amount} card(s)."

    @subscribe(StanceChangedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_stance_changed(self, previous_status, new_status):
        if new_status == StatusType.WRATH:
            add_action(DrawCardsAction(self.amount))


@register("power")
class StudyPower(WatcherPower):
    text_name = "Study"
    text_description = "At the end of your turn, shuffle {amount} Insight into your draw pile."

    def on_turn_end(self):
        super().on_turn_end()
        from cards.watcher import Insight

        for _ in range(max(0, self.amount)):
            add_action(AddCardAction(Insight(), dest_pile="draw_pile"))


@register("power")
class WaveOfTheHandPower(WatcherPower):
    text_name = "Wave of the Hand"
    text_description = "Whenever you gain Block this turn, apply {amount} Weak to all enemies."

    def on_gain_block(self, amount: int, player=None, source=None, card=None):
        from engine.game_state import game_state

        if amount <= 0 or self.owner is None:
            return
        for enemy in list(game_state.current_combat.enemies if game_state.current_combat else []):
            if enemy.is_dead():
                continue
            add_action(ApplyPowerAction(WeakPower(amount=self.amount, duration=self.amount, owner=enemy), enemy))


@register("power")
class MasterRealityPower(WatcherPower):
    text_name = "Master Reality"
    text_description = "Whenever a card is created during combat, upgrade it."
    stack_type = StackType.PRESENCE

    @subscribe(CardAddedToPileMessage, priority=MessagePriority.PLAYER_POWER)
    def on_card_added(self, card, dest_pile="deck"):
        if card is None or not getattr(card, "can_upgrade", None):
            return
        if dest_pile == "deck":
            return
        if card.can_upgrade():
            card.upgrade()


@register("power")
class DevaPower(WatcherPower):
    text_name = "Deva"
    text_description = "At the start of your turn, gain Energy, then increase this by 1."
    stack_type = StackType.LINKED
    amount_equals_duration = True

    def on_turn_start(self):
        gain = max(0, self.amount)
        if gain > 0 and self.owner is not None:
            add_action(GainEnergyAction(gain))
        self.amount += 1


@register("power")
class BlasphemerPower(WatcherPower):
    text_name = "Blasphemer"
    text_description = "At the start of your next turn, die."
    stack_type = StackType.PRESENCE

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.armed = True

    def on_turn_start(self):
        if self.owner is None or not self.armed:
            return
        self.armed = False
        add_actions(
            [
                LoseHPAction(amount=self.owner.hp, target=self.owner, source=self),
                RemovePowerAction("Blasphemer", self.owner),
            ]
        )


@register("power")
class OmegaPower(WatcherPower):
    text_name = "Omega"
    text_description = "At the end of your turn, deal {amount} damage to ALL enemies."
    stack_type = StackType.MULTI_INSTANCE

    def on_turn_end(self):
        super().on_turn_end()
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        for enemy in list(game_state.current_combat.enemies if game_state.current_combat else []):
            if enemy.is_dead():
                continue
            add_action(DealDamageAction(self.amount, target=enemy, source=player))


@register("power")
class WreathOfFlamePower(WatcherPower):
    text_name = "Wreath of Flame"
    text_description = "Your next Attack deals {amount} additional damage."
    modify_phase = DamagePhase.ADDITIVE

    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        if getattr(card, "card_type", None) == CardType.ATTACK:
            return base_damage + self.amount
        return base_damage

    def on_card_play(self, card, player, targets):
        if getattr(card, "card_type", None) == CardType.ATTACK and self.owner is not None:
            add_action(RemovePowerAction("Wreath of Flame", self.owner))


@register("power")
class MarkPower(WatcherPower):
    text_name = "Mark"
    text_description = "When triggered, lose HP equal to Mark."
    stack_type = StackType.INTENSITY
    is_buff = False


@register("power")
class TalkToTheHandPower(WatcherPower):
    text_name = "Talk to the Hand"
    text_description = "Whenever you attack this enemy, gain {amount} Block."
    is_buff = False

    def on_damage_taken(self, damage, source=None, card=None, player=None, damage_type="direct"):
        from engine.game_state import game_state

        if damage <= 0 or getattr(card, "card_type", None) != CardType.ATTACK:
            return
        if self.owner is None or game_state.player is None:
            return
        add_action(GainBlockAction(self.amount, target=game_state.player, source=card, card=card))


@register("power")
class FastingPower(WatcherPower):
    text_name = "Fasting"
    text_description = "Gain 1 less Energy at the start of each turn."
    stack_type = StackType.PRESENCE

    def on_turn_start(self):
        if self.owner is not None:
            self.owner.gain_energy(-1)


@register("power")
class TemporaryDexterityPower(WatcherPower):
    text_name = "Temporary Dexterity"
    text_description = "Dexterity this turn."

    def on_turn_end(self):
        super().on_turn_end()
        if self.owner is not None:
            dexterity = self.owner.get_power("Dexterity")
            if dexterity is not None:
                dexterity.amount = max(0, dexterity.amount - self.amount)
                if dexterity.amount == 0:
                    self.owner.remove_power("Dexterity")
            self.owner.remove_power("Temporary Dexterity")

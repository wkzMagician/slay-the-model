"""Watcher-specific relics."""

from typing import Any

from actions.card import AddCardAction
from actions.combat import GainBlockAction
from actions.combat_status import ApplyPowerAction
from actions.watcher import ChangeStanceAction, GainMantraAction, ScryAction
from engine.runtime_api import add_action
from powers.definitions.dexterity import DexterityPower
from powers.definitions.watcher import TemporaryDexterityPower
from cards.base import RawLocalStr
from relics.base import Relic
from utils.registry import register
from utils.types import RarityType, StatusType, CardType


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


class WatcherRelic(Relic):
    text_name = ""
    text_description = ""

    def __init__(self):
        super().__init__()
        self.name = self.text_name or self.__class__.__name__

    def local(self, field: str, **kwargs):
        text = self.text_name if field == "name" else self.text_description if field == "description" else ""
        if not text:
            return RawLocalStr("")
        try:
            return RawLocalStr(text.format_map(_SafeFormatDict(kwargs)))
        except Exception:
            return RawLocalStr(text)


@register("relic")
class PureWater(WatcherRelic):
    rarity = RarityType.COMMON
    text_name = "Pure Water"
    text_description = "At the start of each combat, add 1 Miracle to your hand."

    def on_combat_start(self, player, entities):
        from cards.watcher import Miracle

        add_action(AddCardAction(Miracle(), dest_pile="hand"))


@register("relic")
class Damaru(WatcherRelic):
    rarity = RarityType.COMMON
    text_name = "Damaru"
    text_description = "At the start of your turn, gain 1 Mantra."

    def on_player_turn_start(self, player, entities):
        add_action(GainMantraAction(1))


@register("relic")
class Duality(WatcherRelic):
    rarity = RarityType.UNCOMMON
    text_name = "Duality"
    text_description = "Whenever you play an Attack, gain 1 temporary Dexterity."

    def on_card_play(self, card, player, targets):
        if getattr(card, "card_type", None) != CardType.ATTACK:
            return
        add_action(ApplyPowerAction(DexterityPower(amount=1, owner=player), player))
        add_action(ApplyPowerAction(TemporaryDexterityPower(amount=1, duration=1, owner=player), player))


@register("relic")
class TeardropLocket(WatcherRelic):
    rarity = RarityType.UNCOMMON
    text_name = "Teardrop Locket"
    text_description = "Start each combat in Calm."

    def on_combat_start(self, player, entities):
        add_action(ChangeStanceAction(StatusType.CALM))


@register("relic")
class CloakClasp(WatcherRelic):
    rarity = RarityType.RARE
    text_name = "Cloak Clasp"
    text_description = "At the end of your turn, gain 1 Block for each card in your hand."

    def on_player_turn_end(self, player, entities):
        add_action(GainBlockAction(len(player.card_manager.get_pile("hand")), target=player))


@register("relic")
class GoldenEye(WatcherRelic):
    rarity = RarityType.SHOP
    text_name = "Golden Eye"
    text_description = "Whenever you Scry, Scry 2 additional cards."


@register("relic")
class HolyWater(WatcherRelic):
    rarity = RarityType.BOSS
    text_name = "Holy Water"
    text_description = "At the start of each combat, add 3 Miracles to your hand."

    def on_combat_start(self, player, entities):
        from cards.watcher import Miracle

        for _ in range(3):
            add_action(AddCardAction(Miracle(), dest_pile="hand"))


@register("relic")
class VioletLotus(WatcherRelic):
    rarity = RarityType.BOSS
    text_name = "Violet Lotus"
    text_description = "Whenever you exit Calm, gain an additional Energy."


@register("relic")
class Melange(WatcherRelic):
    rarity = RarityType.SHOP
    text_name = "Melange"
    text_description = "On use, Scry 3."

    def on_trigger(self, **kwargs):
        add_action(ScryAction(3))

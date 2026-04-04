from __future__ import annotations

from actions.base import Action
from actions.card import DrawCardsAction
from actions.card_choice import MoveCardAction
from actions.combat import GainEnergyAction
from actions.combat_damage import LoseHPAction
from actions.display import InputRequestAction
from engine.runtime_api import add_action, publish_message
from localization import LocalStr
from utils.option import Option
from utils.registry import register
from utils.types import PilePosType, StatusType


@register("action")
class ChangeStanceAction(Action):
    def __init__(self, status: StatusType):
        self.status = status

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import StanceChangedMessage

        player = game_state.player
        if player is None:
            return

        previous = player.status_manager.status
        if previous == self.status:
            return

        player.status_manager.status = self.status

        bonus_energy = 0
        if previous == StatusType.CALM:
            bonus_energy += 2
            if any(getattr(relic, "idstr", None) == "VioletLotus" for relic in player.relics):
                bonus_energy += 1
        if self.status == StatusType.DIVINITY:
            bonus_energy += 3
        if bonus_energy:
            add_action(GainEnergyAction(bonus_energy))

        publish_message(
            StanceChangedMessage(
                owner=player,
                previous_status=previous,
                new_status=self.status,
            )
        )


@register("action")
class GainMantraAction(Action):
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state
        from powers.definitions.watcher import MantraPower

        player = game_state.player
        if player is None or self.amount <= 0:
            return

        mantra = player.get_power("Mantra")
        if mantra is None:
            mantra = MantraPower(amount=0, owner=player)
            player.add_power(mantra)
        mantra.amount += self.amount
        while mantra.amount >= 10:
            mantra.amount -= 10
            add_action(ChangeStanceAction(StatusType.DIVINITY), to_front=True)


@register("action")
class ScryAction(Action):
    def __init__(self, count: int):
        self.count = count

    def execute(self) -> None:
        from engine.game_state import game_state
        from engine.messages import ScryMessage

        player = game_state.player
        if player is None:
            return

        count = max(0, int(self.count))
        if any(getattr(relic, "idstr", None) == "GoldenEye" for relic in player.relics):
            count += 2
        if count <= 0:
            return

        publish_message(ScryMessage(owner=player, count=count))

        draw_pile = player.card_manager.get_pile("draw_pile")
        preview = list(reversed(draw_pile[-count:]))
        if not preview:
            return

        options = [
            Option(
                name=card.info(),
                actions=[
                    MoveCardAction(
                        card=card,
                        src_pile="draw_pile",
                        dst_pile="discard_pile",
                        position=PilePosType.TOP,
                    )
                ],
            )
            for card in preview
        ]
        add_action(
            InputRequestAction(
                title=LocalStr("watcher.scry", default="Choose cards to discard from Scry"),
                options=options,
                max_select=len(options),
                must_select=False,
            ),
            to_front=True,
        )


@register("action")
class TriggerMarkAction(Action):
    def __init__(self, target):
        self.target = target

    def execute(self) -> None:
        if self.target is None:
            return
        mark = self.target.get_power("Mark")
        if mark is None or mark.amount <= 0:
            return
        add_action(LoseHPAction(amount=mark.amount, target=self.target, source=mark), to_front=True)


@register("action")
class ReturnCardToHandAction(Action):
    def __init__(self, card):
        self.card = card

    def execute(self) -> None:
        from engine.game_state import game_state

        player = game_state.player
        if player is None or self.card is None:
            return
        if player.card_manager.get_card_location(self.card) != "discard_pile":
            return
        player.card_manager.move_to(self.card, "hand", src="discard_pile", pos=PilePosType.TOP)


@register("action")
class SkipEnemyTurnAction(Action):
    def execute(self) -> None:
        from engine.game_state import game_state

        combat = game_state.current_combat
        if combat is not None:
            setattr(combat.combat_state, "skip_enemy_turn_once", True)


@register("action")
class DrawCardsNextTurnAction(Action):
    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        add_action(DrawCardsAction(self.amount), to_front=True)

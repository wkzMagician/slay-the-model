"""The two shuffle phases used by Deep Breath and Reboot."""
from actions.base import Action
from engine.random_streams import get_rng
from engine.runtime_api import add_actions, publish_message
from utils.registry import register


@register("action")
class ShuffleDiscardIntoDrawAction(Action):
    def __init__(self, include_hand: bool = False):
        self.include_hand = include_hand

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is None:
            return
        manager = game_state.player.card_manager
        discard = manager.get_pile("discard_pile")
        get_rng("shuffle").shuffle(discard)
        for card in list(discard):
            manager.move_to(card, "draw_pile", src="discard_pile")
        if self.include_hand:
            hand = manager.get_pile("hand")
            while hand:
                card = get_rng("card_random").choice(hand)
                manager.move_to(card, "draw_pile", src="hand")


@register("action")
class ShuffleDrawPileAction(Action):
    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player is not None:
            get_rng("shuffle").shuffle(game_state.player.card_manager.get_pile("draw_pile"))


@register("action")
class DrawAfterShuffleAction(Action):
    def __init__(self, count: int):
        self.count = count

    def execute(self) -> None:
        from actions.card_lifecycle import DrawCardsAction
        from engine.game_state import game_state

        if game_state.player is None:
            return
        manager = game_state.player.card_manager
        available = len(manager.get_pile("draw_pile")) + len(manager.get_pile("discard_pile"))
        DrawCardsAction(count=min(self.count, available)).execute()


def queue_active_shuffle(*, include_hand: bool = False) -> None:
    """Notify relics when the original preparation action is constructed."""
    from engine.game_state import game_state
    from engine.messages import ShuffleMessage

    if game_state.player is None:
        return
    publish_message(ShuffleMessage(owner=game_state.player))
    add_actions([ShuffleDiscardIntoDrawAction(include_hand), ShuffleDrawPileAction()])

from actions.combat_cards import PlayCardAction
from actions.display import InputRequestAction
from cards.base import Card, RawLocalStr
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.option import Option
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Omniscience(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = 4
    upgrade_cost = 3
    base_exhaust = True
    text_name = "Omniscience"
    text_description = "Choose a card in your hand. Play it twice. Exhaust."

    # todo: 效果不完善。两次打出的这张牌，会被消耗
    def on_play(self, targets: List = []):
        options = []
        for card in list(game_state_module.game_state.player.card_manager.get_pile("hand")):
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

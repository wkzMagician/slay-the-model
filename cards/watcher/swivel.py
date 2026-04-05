from actions.card_choice import SetCostUntilEndOfTurnAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_action
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Swivel(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_block = 8
    upgrade_block = 11
    text_name = "Swivel"
    text_description = "Gain {block} Block. Your next Attack this turn costs 0."

    # todo: 效果错误。现在的实现会导致，手牌中所有手牌在当前回合都可以免费打出。应当更改为：获得一个能力，这个能力会记录手牌中所有的攻击牌，以及它们原来的cost_for_this_turn。
    # 在打出牌之后，power把其它的攻击牌的cost_for_this_turn恢复为原值
    def on_play(self, targets: List = []):
        super().on_play(targets)
        for card in list(game_state_module.game_state.player.card_manager.get_pile("hand")):
            if getattr(card, "card_type", None) == CardType.ATTACK:
                add_action(SetCostUntilEndOfTurnAction(card, 0))

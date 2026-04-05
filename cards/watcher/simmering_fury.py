from actions.combat_status import ApplyPowerAction
from actions.watcher import ChangeStanceAction
from cards.base import Card
import engine.game_state as game_state_module
from engine.runtime_api import add_actions
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from typing import List
from utils.registry import register
from utils.types import CardType, RarityType, StatusType, TargetType

@register("card")
class SimmeringFury(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"next_draw": 2}
    upgrade_magic = {"next_draw": 3}
    text_name = "Simmering Fury"
    text_description = "Enter Wrath. Next turn, draw {magic.next_draw} cards."

    # todo: 效果错误。应当是：在下一个回合，进入愤怒并抽牌
    def on_play(self, targets: List = []):
        player = game_state_module.game_state.player
        add_actions(
            [
                ChangeStanceAction(StatusType.WRATH),
                ApplyPowerAction(DrawCardNextTurnPower(amount=self.get_magic_value("next_draw"), duration=1, owner=player), player),
            ]
        )

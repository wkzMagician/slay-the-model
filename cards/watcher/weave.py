from actions.watcher import ReturnCardToHandAction
from cards.base import Card
from engine.messages import ScryMessage
from engine.runtime_api import add_action
from engine.subscriptions import MessagePriority, subscribe
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class Weave(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Weave"
    text_description = "Deal {damage} damage. Whenever you Scry, return this from your discard pile to your hand."

    @subscribe(ScryMessage, priority=MessagePriority.CARD)
    def on_scry(self, count):
        add_action(ReturnCardToHandAction(self))

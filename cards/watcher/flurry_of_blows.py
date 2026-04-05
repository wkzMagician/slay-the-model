from actions.watcher import ReturnCardToHandAction
from cards.base import Card
from engine.messages import StanceChangedMessage
from engine.runtime_api import add_action
from engine.subscriptions import MessagePriority, subscribe
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class FlurryOfBlows(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.COMMON
    base_cost = 0
    base_damage = 4
    upgrade_damage = 6
    text_name = "Flurry of Blows"
    text_description = "Deal {damage} damage. Whenever you change stances, return this from your discard pile to your hand."

    @subscribe(StanceChangedMessage, priority=MessagePriority.CARD)
    def on_stance_changed(self, previous_status, new_status):
        add_action(ReturnCardToHandAction(self))

from cards.watcher._base import *

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

from cards.watcher._base import *

@register("card")
class Scrawl(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 1
    base_exhaust = True
    text_name = "Scrawl"
    text_description = "Draw cards until your hand is full. Exhaust."

    def on_play(self, targets: List = []):
        player = _player()
        draw_needed = max(0, player.card_manager.HAND_LIMIT - len(player.card_manager.get_pile("hand")))
        if draw_needed:
            add_action(DrawCardsAction(draw_needed))

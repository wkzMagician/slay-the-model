from cards.watcher._base import *

@register("card")
class ForeignInfluence(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 0
    base_exhaust = True
    text_name = "Foreign Influence"
    text_description = "Choose 1 of 3 attacks from any color to add to your hand. It costs 0 this turn. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChooseAddRandomCardAction(total=3, card_type=CardType.ATTACK, cost_until_end_of_turn=0))

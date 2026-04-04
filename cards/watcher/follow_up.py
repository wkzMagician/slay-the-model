from cards.watcher._base import *

@register("card")
class FollowUp(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 11
    text_name = "Follow-Up"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, gain 1 Energy."

    def on_play(self, targets: List = []):
        previous = _last_played_card()
        super().on_play(targets)
        if previous is not None and getattr(previous, "card_type", None) == CardType.ATTACK:
            add_action(GainEnergyAction(1))

from cards.watcher._base import *

@register("card")
class SpiritShield(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 2
    base_magic = {"per_card": 3}
    upgrade_magic = {"per_card": 4}
    text_name = "Spirit Shield"
    text_description = "Gain Block equal to {magic.per_card} for each card in your hand."

    def on_play(self, targets: List = []):
        amount = len(_player().card_manager.get_pile("hand")) * self.get_magic_value("per_card")
        add_action(GainBlockAction(amount, target=_player()))

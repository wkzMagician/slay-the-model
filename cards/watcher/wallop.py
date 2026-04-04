from cards.watcher._base import *

@register("card")
class Wallop(WatcherAttack):
    rarity = RarityType.UNCOMMON
    base_cost = 2
    base_damage = 9
    upgrade_damage = 12
    text_name = "Wallop"
    text_description = "Deal {damage} damage. Gain Block equal to damage dealt."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        if target is not None:
            predicted = resolve_potential_damage(self.damage, _player(), target, card=self)
            add_action(GainBlockAction(predicted, target=_player()))

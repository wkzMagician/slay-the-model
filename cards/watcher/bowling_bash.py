from cards.watcher._base import *

@register("card")
class BowlingBash(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 7
    upgrade_damage = 10
    text_name = "Bowling Bash"
    text_description = "Deal {damage} damage for each enemy in combat."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(max(1, len(_alive_enemies()))):
            add_action(AttackAction(self.damage, target=target, source=_player(), damage_type="attack", card=self))

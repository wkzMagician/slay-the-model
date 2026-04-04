from cards.watcher._base import *

@register("card")
class Ragnarok(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 3
    base_damage = 5
    upgrade_damage = 6
    base_attack_times = 5
    upgrade_attack_times = 6
    text_name = "Ragnarok"
    text_description = "Deal {damage} damage to a random enemy {attack_times} times."

    def on_play(self, targets: List = []):
        import random

        enemies = _alive_enemies()
        for _ in range(self.attack_times):
            if enemies:
                add_action(AttackAction(self.damage, target=random.choice(enemies), source=_player(), damage_type="attack", card=self))

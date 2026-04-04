from cards.watcher._base import *

@register("card")
class Expunger(WatcherAttack):
    rarity = RarityType.SPECIAL
    base_cost = 1
    base_damage = 9
    base_exhaust = True
    text_name = "Expunger"
    text_description = "Deal {damage} damage X times. Exhaust."

    def __init__(self, hits: int = 1, **kwargs):
        self.hits = max(1, hits)
        super().__init__(**kwargs)

    def get_combat_description(self, target=None):
        player = _player()
        damage = self.damage
        if player is not None and target is not None:
            damage = resolve_potential_damage(self.damage, player, target, card=self)
        return RawLocalStr(f"Deal {damage} damage {self.hits} times. Exhaust.")

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        for _ in range(self.hits):
            add_action(AttackAction(self.damage, target=target, source=_player(), damage_type="attack", card=self))

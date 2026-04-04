from cards.watcher._base import *

@register("card")
class SashWhip(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"weak": 1}
    upgrade_magic = {"weak": 2}
    text_name = "Sash Whip"
    text_description = "Deal {damage} damage. If the previous card played this turn was an Attack, apply {magic.weak} Weak."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        previous = _last_played_card()
        super().on_play(targets)
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.ATTACK:
            return
        amount = self.get_magic_value("weak")
        add_action(ApplyPowerAction(WeakPower(amount=amount, duration=amount, owner=target), target))

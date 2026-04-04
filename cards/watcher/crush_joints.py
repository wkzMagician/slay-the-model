from cards.watcher._base import *

@register("card")
class CrushJoints(WatcherAttack):
    rarity = RarityType.COMMON
    base_cost = 1
    base_damage = 8
    upgrade_damage = 10
    base_magic = {"vuln": 1}
    upgrade_magic = {"vuln": 2}
    text_name = "Crush Joints"
    text_description = "Deal {damage} damage. If the previous card played this turn was a Skill, apply {magic.vuln} Vulnerable."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        super().on_play(targets)
        previous = _last_played_card()
        if target is None or previous is None or getattr(previous, "card_type", None) != CardType.SKILL:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))

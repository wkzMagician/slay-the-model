from cards.watcher._base import *

@register("card")
class Indignation(WatcherSkill):
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"vuln": 3}
    upgrade_magic = {"vuln": 5}
    text_name = "Indignation"
    text_description = "Apply {magic.vuln} Vulnerable."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        amount = self.get_magic_value("vuln")
        add_action(ApplyPowerAction(VulnerablePower(amount=amount, duration=amount, owner=target), target))

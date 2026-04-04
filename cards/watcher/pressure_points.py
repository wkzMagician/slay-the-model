from cards.watcher._base import *

@register("card")
class PressurePoints(WatcherSkill):
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_SELECT
    base_cost = 1
    base_magic = {"mark": 8}
    upgrade_magic = {"mark": 11}
    text_name = "Pressure Points"
    text_description = "Apply {magic.mark} Mark. ALL enemies lose HP equal to their Mark."

    def on_play(self, targets: List = []):
        target = targets[0] if targets else None
        if target is None:
            return
        add_action(ApplyPowerAction(MarkPower(amount=self.get_magic_value("mark"), owner=target), target))
        for enemy in _alive_enemies():
            add_action(TriggerMarkAction(enemy))

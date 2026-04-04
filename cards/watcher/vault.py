from cards.watcher._base import *

@register("card")
class Vault(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 3
    upgrade_cost = 2
    base_exhaust = True
    text_name = "Vault"
    text_description = "End your turn. Take another turn after this one."

    def on_play(self, targets: List = []):
        add_actions([SkipEnemyTurnAction(), EndTurnAction()])

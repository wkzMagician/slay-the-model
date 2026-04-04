from cards.watcher._base import *

@register("card")
class LessonLearned(WatcherAttack):
    rarity = RarityType.RARE
    base_cost = 2
    base_damage = 10
    upgrade_damage = 13
    text_name = "Lesson Learned"
    text_description = "Deal {damage} damage. If Fatal, upgrade a card in your deck."

    def on_fatal(self, damage, target=None, card=None, damage_type: str = "direct"):
        if card is not self:
            return
        for candidate in _player().card_manager.get_pile("deck"):
            if candidate.can_upgrade():
                candidate.upgrade()
                break

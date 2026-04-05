from cards.base import Card
import engine.game_state as game_state_module
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class LessonLearned(Card):
    card_type = CardType.ATTACK
    target_type = TargetType.ENEMY_SELECT
    rarity = RarityType.RARE
    base_cost = 2
    base_damage = 10
    upgrade_damage = 13
    text_name = "Lesson Learned"
    text_description = "Deal {damage} damage. If Fatal, upgrade a card in your deck."

    def on_fatal(self, damage, target=None, card=None, damage_type: str = "direct"):
        if card is not self:
            return
        for candidate in game_state_module.game_state.player.card_manager.get_pile("deck"):
            if candidate.can_upgrade():
                candidate.upgrade()
                break

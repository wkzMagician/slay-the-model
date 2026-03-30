"""Corpse Explosion death trigger power."""

from actions.combat import DealDamageAction
from engine.messages import CreatureDiedMessage
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class CorpseExplosionPower(Power):
    name = 'Corpse Explosion'
    description = 'When this enemy dies, deal damage to all enemies equal to its max HP.'
    stack_type = StackType.PRESENCE
    is_buff = False

    def __init__(self, amount: int = 0, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    @subscribe(CreatureDiedMessage, priority=MessagePriority.REACTION)
    def on_death(self, message):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        creature = getattr(message, "creature", None)
        if self.owner is None or creature is not self.owner or game_state.current_combat is None:
            return
        damage = self.owner.max_hp
        actions = [
            DealDamageAction(
                damage=damage,
                target=enemy,
                source=getattr(message, "source", None),
                card=getattr(message, "card", None),
            )
            for enemy in game_state.current_combat.enemies
            if enemy is not self.owner and enemy.hp > 0
        ]
        add_actions(actions)

"""Bronze Orb minion intentions."""

from typing import List
from enemies.intention import Intention
from actions.combat import AttackAction, GainBlockAction


class Steal(Intention):
    """Steal a card from player's draw pile."""

    def __init__(self, enemy):
        super().__init__("Steal", enemy)
        # Note: Card stealing is complex, this is a simplified implementation

    def execute(self) -> List:
        """Steal a random high-rarity card from draw pile."""
        # TODO: Implement card stealing mechanic
        # This requires accessing game_state.player.draw_pile
        # and moving a card to the Bronze Orb's "stolen" state
        return []


class SupportBeam(Intention):
    """Give Bronze Automaton 11 Block."""

    def __init__(self, enemy):
        super().__init__("Support Beam", enemy)
        self.base_block = 12

    def execute(self) -> List:
        """Give block to Bronze Automaton."""
        from engine.game_state import game_state
        actions = []
        # Find the Bronze Automaton (parent) in combat
        if game_state.current_combat:
            for e in game_state.current_combat.enemies:
                if e.__class__.__name__ == "BronzeAutomaton" and e.hp > 0:
                    actions.append(GainBlockAction(self.base_block, e))
                    break
        return actions


class Beam(Intention):
    """Deal 8 damage."""

    def __init__(self, enemy):
        super().__init__("Beam", enemy)
        self.base_damage = 8

    def execute(self) -> List:
        """Deal damage to player."""
        from engine.game_state import game_state
        damage = self.enemy.calculate_damage(self.base_damage)
        return [AttackAction(damage, game_state.player, self.enemy, "attack")]

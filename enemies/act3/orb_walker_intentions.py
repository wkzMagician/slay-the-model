"""Orb Walker intentions."""

from enemies.intention import Intention
from actions.combat import AttackAction


class Laser(Intention):
    """Laser attack - deals damage and adds Burns."""

    def __init__(self, enemy):
        super().__init__("Laser", enemy)
        self.base_damage = 10
        self.base_damage_asc = 11

    def execute(self):
        """Execute Laser: Deals damage and adds Burns to draw and discard pile."""
        from engine.game_state import game_state
        from cards.status_cards import Burn

        damage = self.get_damage()
        actions = [
            AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]

        # Add Burn to draw pile
        burn1 = Burn()
        game_state.player.draw_pile.append(burn1)

        # Add Burn to discard pile
        burn2 = Burn()
        game_state.player.discard_pile.append(burn2)

        return actions


class Claw(Intention):
    """Claw attack - deals damage."""

    def __init__(self, enemy):
        super().__init__("Claw", enemy)
        self.base_damage = 15
        self.base_damage_asc = 16

    def execute(self):
        """Execute Claw: Deals damage."""
        from engine.game_state import game_state

        damage = self.get_damage()
        return [
            AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]

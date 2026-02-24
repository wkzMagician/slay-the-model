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
        from engine.game_state import game_state
        from utils.types import RarityType
        
        if not game_state.player:
            return []
        
        card_manager = game_state.player.card_manager
        draw_pile = card_manager.get_pile('draw_pile')
        
        if not draw_pile:
            return []
        
        # Prefer stealing higher rarity cards
        rarity_priority = [RarityType.RARE, RarityType.UNCOMMON, RarityType.COMMON, RarityType.STARTER]
        
        for rarity in rarity_priority:
            # Find cards of this rarity
            candidates = [c for c in draw_pile if c.rarity == rarity]
            if candidates:
                import random
                stolen_card = random.choice(candidates)
                # Remove from draw pile
                card_manager.remove_from_pile(stolen_card, 'draw_pile')
                # Store in enemy's stolen cards
                self.enemy.stolen_cards.append(stolen_card)
                return []  # No actions needed, card is stolen
        
        # Fallback: steal any card
        import random
        stolen_card = random.choice(draw_pile)
        card_manager.remove_from_pile(stolen_card, 'draw_pile')
        self.enemy.stolen_cards.append(stolen_card)
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
        return [AttackAction(self.base_damage, game_state.player, self.enemy, "attack")]

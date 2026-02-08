from typing import List, Optional, Tuple
from actions.base import Action
from localization import Localizable
from utils.types import RarityType

class Relic(Localizable):
    """Base class for all relics in the game.
    
    Relics provide passive or active effects that trigger during
    various game phases (combat, card play, damage, etc.).
    """
    localization_prefix = "relics"
    localizable_fields: Tuple[str, ...] = ("name", "description")
    rarity = RarityType.COMMON

    def __init__(self):
        pass
    
    # ==================== Phase Hooks ====================
    
    def on_combat_start(self, player, entities) -> List[Action]:
        """Called at the start of combat.
        
        Returns:
            List of actions to execute after combat starts.
        """
        return []

    def on_combat_end(self, player, entities) -> List[Action]:
        """Called at the end of combat.
        
        Returns:
            List of actions to execute after combat ends.
        """
        return []

    def on_player_turn_start(self, player, entities) -> List[Action]:
        """Called at the start of player's turn.
        
        Returns:
            List of actions to execute at turn start.
        """
        return []

    def on_player_turn_end(self, player, entities) -> List[Action]:
        """Called at the end of player's turn.
        
        Returns:
            List of actions to execute at turn end.
        """
        return []

    def on_enemy_turn_start(self, enemy, player, entities) -> List[Action]:
        """Called at the start of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn start.
        """
        return []

    def on_enemy_turn_end(self, enemy, player, entities) -> List[Action]:
        """Called at the end of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn end.
        """
        return []
    
    # ==================== Card Hooks ====================
    
    def on_card_play(self, card, player, entities) -> List[Action]:
        """Called when a card is played.
        
        Returns:
            List of actions to execute after card is played.
        """
        return []
    
    def on_card_draw(self, card, player, entities) -> List[Action]:
        """Called when a card is drawn.
        
        Returns:
            List of actions to execute after card is drawn.
        """
        return []
    
    def on_card_discard(self, card, player, entities) -> List[Action]:
        """Called when a card is discarded.
        
        Returns:
            List of actions to execute after card is discarded.
        """
        return []
    
    def on_card_exhaust(self, card, player, entities) -> List[Action]:
        """Called when a card is exhausted.
        
        Returns:
            List of actions to execute after card is exhausted.
        """
        return []

    # ==================== Stat Hooks ====================
    
    def on_damage_dealt(self, damage, target, player, entities) -> List[Action]:
        """Called when damage is dealt.
        
        Args:
            damage: Original damage amount
            target: Entity receiving damage
            player: Player instance
            entities: All entities in combat
            
        Returns:
            List of actions to execute when damage is dealt
        """
        return []

    def on_damage_taken(self, damage, source, player, entities) -> List[Action]:
        """Called when damage is taken.
        
        Args:
            damage: Original damage amount
            source: Entity dealing damage
            player: Player instance
            entities: All entities in combat
            
        Returns:
            List of actions to execute when damage is taken
        """
        return []

    def on_heal(self, heal_amount, player, entities) -> List[Action]:
        """Called when healing occurs.
        
        Args:
            heal_amount: Original heal amount
            player: Player instance
            entities: All entities in combat
            
        Returns:
            List of actions to execute when healing occurs
        """
        return []

    # ==================== Active Trigger ====================
    
    def on_trigger(self, **kwargs) -> List[Action]:
        """Manually trigger relic effect.
        
        This is called for relics with active effects that can be
        triggered by player interaction (e.g., clicking on relic).
        
        Args:
            **kwargs: Additional context parameters
            
        Returns:
            List of actions to execute
        """
        return []

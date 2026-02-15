"""Hexaghost (Boss) specific intentions."""

from typing import List, TYPE_CHECKING

from enemies.intention import Intention

if TYPE_CHECKING:
    from enemies.base import Enemy
    from actions.base import Action


class ActivateIntention(Intention):
    """Activate - Does nothing."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("activate", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Activate: does nothing."""
        return []


class DividerIntention(Intention):
    """Divider - Deals (N+1)×6 damage where N = Player HP / 12."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("divider", enemy)
    
    def execute(self) -> List['Action']:
        """Execute Divider: damage based on player's HP."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        # Calculate damage based on player's HP
        player_hp = game_state.player.hp
        n = player_hp // 12
        damage = (n + 1) * 6
        
        return [
            AttackAction(
                damage=damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
    
    @property
    def description(self):
        """Custom description for Divider."""
        from localization import LocalStr
        from engine.game_state import game_state
        
        if game_state and game_state.player:
            player_hp = game_state.player.hp
            n = player_hp // 12
            damage = (n + 1) * 6
            return LocalStr(f"Deals {damage} damage.")
        return LocalStr("Deals damage based on your HP.")


class SearIntention(Intention):
    """Sear - Deals 6 damage and adds 1 Burn to discard (2 Burns on A19+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("sear", enemy)
        self.base_damage = 6
        self._burn_count = 1
    
    def execute(self) -> List['Action']:
        """Execute Sear: deals 6 damage and adds Burn cards."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from engine.game_state import game_state
        from utils.registry import get_registered
        
        if not game_state or not game_state.player:
            return []
        
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
        ]
        
        # Add Burn cards
        try:
            BurnCard = get_registered("card", "Burn")
            if BurnCard:
                for _ in range(self._burn_count):
                    actions.append(AddCardAction(card=BurnCard(), dest_pile="discard"))
        except:
            pass
        
        return actions


class TackleIntention(Intention):
    """Tackle - Deals 5 damage 2 times (6×2 on A4+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("tackle", enemy)
        self.base_damage = 5
        self._hits = 2
    
    def execute(self) -> List['Action']:
        """Execute Tackle: deals damage multiple times."""
        from actions.combat import AttackAction
        from engine.game_state import game_state
        
        if not game_state or not game_state.player:
            return []
        
        return [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
            for _ in range(self._hits)
        ]


class InflameIntention(Intention):
    """Inflame - Gains 12 Block and 2 Strength (3 Strength on A19+)."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("inflame", enemy)
        self.base_block = 12
        self.base_strength_gain = 2
    
    def execute(self) -> List['Action']:
        """Execute Inflame: gains Block and Strength."""
        from actions.combat import GainBlockAction, ApplyPowerAction
        
        return [
            GainBlockAction(
                block=self.base_block,
                target=self.enemy
            ),
            ApplyPowerAction(
                power="strength",
                target=self.enemy,
                amount=self.base_strength_gain,
                duration=0
            )
        ]


class InfernoIntention(Intention):
    """Inferno - Deals 2×6 damage (3×6 on A4+), adds 3 Burn+ to discard."""
    
    def __init__(self, enemy: 'Enemy'):
        super().__init__("inferno", enemy)
        self.base_damage = 6
        self._hits = 2
        self._burn_count = 3
    
    def execute(self) -> List['Action']:
        """Execute Inferno: deals damage and adds upgraded Burn cards."""
        from actions.combat import AttackAction
        from actions.card import AddCardAction
        from engine.game_state import game_state
        from utils.registry import get_registered
        
        if not game_state or not game_state.player:
            return []
        
        actions = [
            AttackAction(
                damage=self.base_damage,
                target=game_state.player,
                source=self.enemy,
                damage_type="attack",
            )
            for _ in range(self._hits)
        ]
        
        # Add Burn+ cards
        try:
            BurnCard = get_registered("card", "Burn")
            if BurnCard:
                for _ in range(self._burn_count):
                    burn = BurnCard()
                    if hasattr(burn, 'upgrade'):
                        burn.upgrade()
                    actions.append(AddCardAction(card=burn, dest_pile="discard"))
        except:
            pass
        
        return actions

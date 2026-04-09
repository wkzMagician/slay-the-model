from typing import List, Optional, Tuple
from actions.base import Action
from localization import Localizable, t
from engine.messages import (
    AnyHpLostMessage,
    BlockGainedMessage,
    CardPlayedMessage,
    CardAddedToPileMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CardExhaustedMessage,
    CombatEndedMessage,
    CombatStartedMessage,
    DamageDealtMessage,
    DirectHpLossMessage,
    EliteVictoryMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    PhysicalAttackDealtMessage,
    PhysicalAttackTakenMessage,
    RelicObtainedMessage,
    PlayerTurnPostDrawMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    ShuffleMessage,
    ShopEnteredMessage,
)
from engine.subscriptions import MessagePriority, subscribe
from utils.types import RarityType
from utils.damage_phase import DamagePhase

class Relic(Localizable):
    """Base class for all relics in the game.
    
    Relics provide passive or active effects that trigger during
    various game phases (combat, card play, damage, etc.).
    """
    localization_prefix = "relics"
    localizable_fields: Tuple[str, ...] = ("name", "description")
    rarity = RarityType.COMMON
    
    # Damage modification phase (same as Power)
    # ADDITIVE: Applied first (e.g., +3 damage)
    # MULTIPLICATIVE: Applied second (e.g., 2x damage)
    # CAPPING: Applied last (e.g., cap at 1)
    modify_phase: DamagePhase = DamagePhase.ADDITIVE

    def __init__(self):
        self.namespace = self._resolve_namespace()

    def _resolve_namespace(self) -> str:
        """Infer relic namespace from module path.

        Character relics live under ``relics.character.<character>``.
        All other relics are global and use ``any``.
        """
        module = getattr(self.__class__, "__module__", "")
        parts = module.split(".")
        if "character" in parts:
            idx = parts.index("character")
            if idx + 1 < len(parts):
                return parts[idx + 1]
        return "any"

    def combat_enemies(self) -> list:
        """Return the current combat enemy list, or an empty list outside combat."""
        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None)
        if combat is None:
            return []
        return list(getattr(combat, "enemies", []) or [])

    def alive_enemies(self) -> list:
        """Return living enemies in the current combat."""
        return [enemy for enemy in self.combat_enemies() if not enemy.is_dead()]
    
    @subscribe(RelicObtainedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_obtain(self):
        return
    
    # ==================== Phase Hooks ====================
    
    @subscribe(CombatStartedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_combat_start(self, floor: int):
        """Called at the start of combat.
        
        Returns:
            List of actions to execute after combat starts.
        """
        return

    @subscribe(CombatEndedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_combat_end(self):
        """Called at the end of combat.
        
        Returns:
            List of actions to execute after combat ends.
        """
        return
    
    @subscribe(EliteVictoryMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_elite_victory(self):
        """Called when player defeats an elite enemy.
        
        Returns:
            List of actions to execute after elite victory.
        """
        return

    @subscribe(PlayerTurnStartedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_player_turn_start(self):
        """Called at the start of player's turn.
        
        Returns:
            List of actions to execute at turn start.
        """
        return

    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_player_turn_end(self):
        """Called at the end of player's turn.
        
        Returns:
            List of actions to execute at turn end.
        """
        return

    def on_enemy_turn_start(self, enemy, player):
        """Called at the start of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn start.
        """
        return

    def on_enemy_turn_end(self, enemy, player):
        """Called at the end of enemy's turn.
        
        Returns:
            List of actions to execute at enemy turn end.
        """
        return

    @subscribe(ShopEnteredMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_shop_enter(self):
        """Called when entering a shop room."""
        return
    
    # ==================== Card Hooks ====================
    
    @subscribe(CardPlayedMessage, priority=MessagePriority.REACTION)
    def on_card_play(self, card, targets):
        """Called when a card is played.
        
        Returns:
            List of actions to execute after card is played.
        """
        return
    
    @subscribe(CardDrawnMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_card_draw(self, card):
        """Called when a card is drawn.
        
        Returns:
            List of actions to execute after card is drawn.
        """
        return
    
    @subscribe(CardDiscardedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_card_discard(self, card):
        """Called when a card is discarded.
        
        Returns:
            List of actions to execute after card is discarded.
        """
        return
    
    def on_card_exhaust(self, card, player):
        """Called when a card is exhausted.
        
        Returns:
            List of actions to execute after card is exhausted.
        """
        return

    @subscribe(CardExhaustedMessage, priority=MessagePriority.REACTION)
    def on_card_exhausted(self, card, source_pile=None):
        """Called when a card is exhausted."""
        return

    @subscribe(CardAddedToPileMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_card_added(self, card, dest_pile: str = "deck"):
        """Called when a card is added to a pile."""
        return

    # ==================== Stat Hooks ====================
    
    @subscribe(DamageDealtMessage, priority=MessagePriority.REACTION)
    def on_damage_dealt(self, damage, target, source=None, card=None, damage_type="direct"):
        """Called when damage is dealt.
        
        Args:
            damage: Original damage amount
            target: Entity receiving damage
            player: Player instance
        Returns:
            List of actions to execute when damage is dealt
        """
        return

    @subscribe(PlayerTurnPostDrawMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_player_turn_post_draw(self):
        """Called after the player's normal start-of-turn draw resolves."""
        return

    @subscribe(PhysicalAttackDealtMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_dealt(self, damage, target=None, source=None, card=None, damage_type="physical"):
        """Called when a physical attack deals HP damage."""
        return

    @subscribe(PhysicalAttackTakenMessage, priority=MessagePriority.REACTION)
    def on_physical_attack_taken(self, damage, source=None, card=None, damage_type="physical"):
        """Called when the player loses HP to a physical attack."""
        return

    @subscribe(HealedMessage, priority=MessagePriority.REACTION)
    def on_heal(self, amount, source=None):
        """Called when healing occurs.
        
        Args:
            heal_amount: Original heal amount
            player: Player instance
        Returns:
            List of actions to execute when healing occurs
        """
        return

    @subscribe(DirectHpLossMessage, priority=MessagePriority.REACTION)
    def on_direct_hp_loss(self, amount: int, source=None, card=None):
        """Called when direct HP loss resolves."""
        return

    @subscribe(AnyHpLostMessage, priority=MessagePriority.REACTION)
    def on_any_hp_lost(self, amount: int, source=None, card=None):
        """Called whenever actual HP is lost."""
        return
    
    # ==================== Modification Hooks ====================
    
    def modify_damage_dealt(self, base_damage: int, card=None, target=None) -> int:
        """Modify damage dealt by the player.
        
        Args:
            base_damage: Original damage amount
            card: Card being played (if applicable)
            target: Target receiving damage (if applicable)
            
        Returns:
            Modified damage amount
        """
        return base_damage
    
    def modify_damage_taken(self, base_damage: int, source=None, damage_type: str = "direct") -> int:
        """Modify damage taken by the player.
        
        Args:
            base_damage: Original damage amount
            source: Source dealing damage (if applicable)
            
        Returns:
            Modified damage amount
        """
        return base_damage

    def on_spawn_monster(self, monster, player):
        """Called when a new enemy is added to the current combat."""
        return
    
    def modify_heal(self, base_heal: int) -> int:
        """Modify healing received.
        
        Args:
            base_heal: Original heal amount
            
        Returns:
            Modified heal amount
        """
        return base_heal
    
    def modify_block_gained(self, base_block: int) -> int:
        """Modify block gained.
        
        Args:
            base_block: Original block amount
            
        Returns:
            Modified block amount
        """
        return base_block
    
    def modify_gold_gained(self, base_gold: int) -> int:
        """Modify gold gained.
        
        Args:
            base_gold: Original gold amount
            
        Returns:
            Modified gold amount
        """
        return base_gold
    
    @subscribe(GoldGainedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_gold_gained(self, gold_amount: int):
        """Called when gold is gained.
        
        Args:
            gold_amount: Amount of gold gained
            player: Player instance
            
        Returns:
            List of actions to execute when gold is gained
        """
        return
    
    @subscribe(ShuffleMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_shuffle(self):
        """Called when draw pile is shuffled.
        
        Returns:
            List of actions to execute when shuffling occurs
        """
        return
    
    @subscribe(PotionUsedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_use_potion(self, potion):
        """Called when a potion is used.
        
        Args:
            potion: The potion being used
            player: Player instance
        Returns:
            List of actions to execute when potion is used
        """
        return
    
    @subscribe(PowerAppliedMessage, priority=MessagePriority.REACTION)
    def on_apply_power(self, power, target):
        """Called when a power is applied to a target.
        
        Args:
            power: The power being applied
            target: The creature receiving the power
            player: Player instance
        Returns:
            List of actions to execute when power is applied
        """
        return
 
    # ==================== Active Trigger ====================
    
    def on_trigger(self, **kwargs):
        """Manually trigger relic effect.
        
        This is called for relics with active effects that can be
        triggered by player interaction (e.g., clicking on relic).
        
        Args:
            **kwargs: Additional context parameters
            
        Returns:
            List of actions to execute
        """
        return
    
    def info(self):
        """
        获取遗物的完整信息显示
        
        返回格式：
        RelicName (Rarity: Common)
        Description text
        """
        return self.local("name") + f" ({t('ui.rarity_label', 'Rarity: {rarity}', rarity=self.rarity.value)})\n" + self.local("description")

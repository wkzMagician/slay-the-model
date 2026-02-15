"""Test PenNib relic functionality."""
import pytest
from relics.global_relics.common import PenNib
from powers.definitions import PenNibPower
from actions.combat import ApplyPowerAction
from entities.player import Player
from cards.base import Card
from utils.types import CardType
from engine.game_state import GameState


class TestPenNib:
    """Test PenNib relic - every 10th attack deals double damage."""
    
    def test_pen_nib_initialization(self):
        """PenNib relic should initialize correctly."""
        relic = PenNib()
        assert relic.attacks_played == 0
        assert relic.double_damage_next_attack == False
        assert relic.rarity.name == "COMMON"
    
    def test_pen_nib_resets_on_combat_start(self):
        """PenNib should reset attack counter at combat start."""
        relic = PenNib()
        player = Player(max_hp=70)
        
        # Simulate some attacks
        relic.attacks_played = 5
        
        # Reset on combat start
        actions = relic.on_combat_start(player, [])
        
        # Should reset counter to 0
        assert relic.attacks_played == 0
        assert len(actions) == 1
    
    def test_pen_nib_tracks_attacks(self):
        """PenNib should track attack cards played."""
        relic = PenNib()
        player = Player(max_hp=70)
        
        # Create mock attack card
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=6
        )
        
        # Play 9 attacks - should not trigger power yet
        for i in range(9):
            actions = relic.on_card_play(attack_card, player, [])
            assert len(actions) == 0
            assert relic.attacks_played == i + 1
        
        # 10th attack should trigger the power
        actions = relic.on_card_play(attack_card, player, [])
        assert len(actions) == 1
        assert isinstance(actions[0], ApplyPowerAction)
        assert actions[0].power == "PenNibPower"
        assert actions[0].duration == 1
    
    def test_pen_nib_only_counts_attacks(self):
        """PenNib should only count Attack cards, not Skills or Powers."""
        relic = PenNib()
        player = Player(max_hp=70)
        
        # Create mock cards
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=6
        )
        skill_card = Card(
            name="Defend",
            card_type=CardType.SKILL,
            base_cost=1,
            base_block=5
        )
        
        # Play skill - should not count
        actions = relic.on_card_play(skill_card, player, [])
        assert len(actions) == 0
        assert relic.attacks_played == 0
        
        # Play attack - should count
        actions = relic.on_card_play(attack_card, player, [])
        assert len(actions) == 0
        assert relic.attacks_played == 1
    
    def test_pen_nib_multiple_ten_count_intervals(self):
        """PenNib should trigger on 10th, 20th, 30th attacks, etc."""
        relic = PenNib()
        player = Player(max_hp=70)
        
        # Create mock attack card
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=6
        )
        
        # Test 10th attack
        for i in range(10):
            relic.on_card_play(attack_card, player, [])
        assert relic.attacks_played == 10
        
        # Reset counter for next combat
        relic.attacks_played = 0
        
        # Test 20th attack across two combats
        # First combat: 15 attacks
        for i in range(15):
            actions = relic.on_card_play(attack_card, player, [])
            if i == 9:  # 10th attack
                assert len(actions) == 1
                assert isinstance(actions[0], ApplyPowerAction)
        
        assert relic.attacks_played == 15
        
        # Reset for second combat
        relic.on_combat_start(player, [])
        
        # Second combat: 5 more attacks to reach 20 total
        for i in range(5):
            relic.on_card_play(attack_card, player, [])
        
        # Total attacks played: 15 + 5 = 20
        # But counter resets each combat, so this is the 5th attack of this combat
        assert relic.attacks_played == 5
    
    def test_pen_nib_power_application(self):
        """PenNib should apply PenNibPower to player on 10th attack."""
        relic = PenNib()
        player = Player(max_hp=70)
        
        # Create mock attack card
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=6
        )
        
        # Play 10 attacks
        for i in range(10):
            actions = relic.on_card_play(attack_card, player, [])
        
        # Should have triggered on 10th attack
        assert len(actions) == 1
        assert isinstance(actions[0], ApplyPowerAction)
        assert actions[0].power == "PenNibPower"
        assert actions[0].target == player
        assert actions[0].duration == 1
    
    def test_pen_nib_power_duration(self):
        """PenNibPower should have duration of 1 attack."""
        power = PenNibPower(amount=1, duration=1)
        
        assert power.duration == 1
        assert power.damage_multiplier == 2
        assert power.name == "PenNib"
        assert power.is_buff == True
    
    def test_pen_nib_power_doubles_damage(self):
        """PenNibPower should double attack card damage when played."""
        power = PenNibPower(amount=1, duration=1, owner=Player(max_hp=70))
        
        # Create mock attack card
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=10
        )
        
        original_damage = attack_card.base_damage
        
        # Trigger power on card play
        power.on_card_play(attack_card, None, [])
        
        # Damage should be doubled
        assert attack_card.base_damage == original_damage * 2
        
        # Power should be removed (duration = 0)
        assert power.duration == 0
    
    def test_pen_nib_power_only_affects_attacks(self):
        """PenNibPower should only affect Attack cards, not Skills."""
        power = PenNibPower(amount=1, duration=1, owner=Player(max_hp=70))
        
        # Create mock skill card
        skill_card = Card(
            name="Defend",
            card_type=CardType.SKILL,
            base_cost=1,
            base_block=5
        )
        
        original_block = skill_card.base_block
        
        # Trigger power on card play
        power.on_card_play(skill_card, None, [])
        
        # Skill card should not be affected
        assert skill_card.base_block == original_block
        
        # Power should not be consumed
        assert power.duration == 1
    
    def test_pen_nib_power_removed_after_use(self):
        """PenNibPower should be removed after doubling one attack."""
        power = PenNibPower(amount=1, duration=1, owner=Player(max_hp=70))
        
        # Create mock attack card
        attack_card = Card(
            name="Attack",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=10
        )
        
        # Use power
        power.on_card_play(attack_card, None, [])
        
        # Duration should be 0, indicating power should be removed
        assert power.duration == 0


class TestPenNibIntegration:
    """Integration tests for PenNib in combat scenario."""
    
    def test_pen_nib_full_combat_scenario(self):
        """Test PenNib through a full combat scenario."""
        from enemies.base import Enemy
        from engine.combat import Combat
        from utils.types import CombatType
        
        # Setup
        relic = PenNib()
        player = Player(max_hp=70)
        player.relics = [relic]
        
        enemy = Enemy(name="Test Enemy", max_hp=50, damage=8)
        
        # Mock game state
        game_state = GameState()
        game_state.player = player
        game_state.current_floor = 1
        
        # Simulate combat start - should reset counter
        actions = relic.on_combat_start(player, [])
        assert relic.attacks_played == 0
        
        # Create attack card
        attack_card = Card(
            name="Strike",
            card_type=CardType.ATTACK,
            base_cost=1,
            base_damage=6
        )
        
        # Play 9 attacks - no power
        for i in range(9):
            actions = relic.on_card_play(attack_card, player, [])
            assert len(actions) == 0
        
        assert relic.attacks_played == 9
        
        # 10th attack - should apply PenNibPower
        actions = relic.on_card_play(attack_card, player, [])
        assert len(actions) == 1
        assert isinstance(actions[0], ApplyPowerAction)
        assert actions[0].power == "PenNibPower"
        
        # Create power instance to verify it works
        power = PenNibPower(amount=1, duration=1, owner=player)
        test_card = Card(name="Test Attack", card_type=CardType.ATTACK, 
                        base_cost=1, base_damage=12)
        
        original_damage = test_card.base_damage
        power.on_card_play(test_card, player, [])
        
        # Damage should be doubled
        assert test_card.base_damage == original_damage * 2
"""Basic tests for relic implementations."""
import pytest
from relics.base import Relic
from powers.definitions import BufferPower
from actions.card import UpgradeRandomCardAction
from actions.combat import GainBlockAction, GainEnergyAction, ApplyPowerAction, RemovePowerAction

# Top-level imports for all test classes
from player.player import Player
from engine.game_state import GameState
from powers.definitions import VulnerablePower

# Common relics
from relics.global_relics.common import Akabeko, Anchor, BronzeScales

# Uncommon relics
from relics.global_relics.uncommon import BlueCandle, Pantograph, Sundial

# Rare relics
from relics.global_relics.rare import DeadBranch

# Boss relics
from relics.global_relics.boss import SneckoEye

# Ironclad relics
from relics.character.ironclad import ChampionBelt, OrangePellets, BurningBlood as IroncladBurningBlood

class TestNewRelicFeatures:
    
    def test_champion_belt_applies_weak_on_vulnerable(self):
        """ChampionBelt should apply Weak to player when Vulnerable is applied to enemy"""
        from relics.character.ironclad import ChampionBelt
        from player.player import Player
        from powers.definitions import VulnerablePower
        from engine.game_state import GameState
        
        # Mock game state
        from engine.game_state import game_state
        game_state.__init__()  # Reset singleton for test
        player = Player(max_hp=70)
        game_state.player = player
        
        # Add relics
        champion_belt = ChampionBelt()
        game_state.player.relics = [champion_belt]
        
        # Mock enemy with Vulnerable
        enemy = Player(max_hp=50)
        enemy.powers = []
        
        # Apply Vulnerable to enemy
        apply_vulnerable = ApplyPowerAction(power="Vulnerable", target=enemy, amount=1, duration=2)
        
        # Get relic response when Vulnerable is applied
        actions = champion_belt.on_apply_power(
            power=VulnerablePower(amount=1, duration=2),
            target=enemy,
            player=player,
            entities=[]
        )
        
        # Should return two actions: Apply Weak to player and Apply Weak to player
        assert len(actions) == 2
        assert any(isinstance(a, ApplyPowerAction) for a in actions)
        
        # Check that Weak is applied to player
        weak_to_player = [a for a in actions if a.power == "Weak"]
        assert len(weak_to_player) == 1
        assert isinstance(weak_to_player[0], ApplyPowerAction)
        assert weak_to_player[0].amount == 1
    
    def test_orange_pellets_removes_debuffs(self):
        """OrangePellets should remove all debuffs when Power/Attack/Skill played in same turn"""
        from relics.character.ironclad import OrangePellets
        from player.player import Player
        from actions.combat import RemovePowerAction
        from utils.types import CardType
        from powers.definitions import WeakPower
        
        # Mock game state
        from engine.game_state import game_state
        game_state.__init__()  # Reset singleton for test
        player = Player(max_hp=70)
        game_state.player = player
        
        # Add relic
        orange_pellets = OrangePellets()
        game_state.player.relics = [orange_pellets]
        
        # Add debuffs to player
        weak = WeakPower(amount=1, duration=2)
        vulnerable = VulnerablePower(amount=1, duration=2)
        player.powers.extend([weak, vulnerable])
        
        # Create mock cards for testing
        from cards.base import Card
        from utils.types import CardType
        
        power_card = Card(name="TestPower", card_type=CardType.POWER)
        attack_card = Card(name="TestAttack", card_type=CardType.ATTACK)
        skill_card = Card(name="TestSkill", card_type=CardType.SKILL)
        
        # Play a Power card
        orange_pellets.on_card_play(power_card, player, [])
        
        # Play an Attack card (should not complete yet)
        orange_pellets.on_card_play(attack_card, player, [])
        
        # Play a Skill card - this should remove all debuffs
        actions = orange_pellets.on_card_play(skill_card, player, [])
        # Execute the returned actions
        for action in actions:
            action.execute()
        
        assert len(actions) == 2
        assert all(isinstance(a, RemovePowerAction) for a in actions)
        
        # Verify debuffs were removed
        for power in player.powers:
            assert power.__class__.__name__ not in ["WeakPower", "VulnerablePower"]
    
    def test_pantograph_heals_on_boss_combat_start(self):
        """Pantograph should heal 25 HP at start of boss combat"""
        from relics.global_relics.uncommon import Pantograph
        from player.player import Player
        from actions.combat import HealAction, ApplyPowerAction
        from utils.types import CombatType
        from engine.game_state import GameState
        
        # Mock game state with boss combat
        from engine.game_state import game_state
        game_state.__init__()  # Reset singleton for test
        player = Player(max_hp=70)
        game_state.player = player
        
        # Add relic
        pantograph = Pantograph()
        game_state.player.relics = [pantograph]
        
        # Create mock boss combat
        from engine.combat_state import CombatState
        combat_state = CombatState()
        combat_state.combat_type = CombatType.BOSS
        game_state.current_combat = combat_state
        
        # Get combat start actions
        actions = pantograph.on_combat_start(player, [])
        
        # Should return one action: Apply Regeneration for 25 HP
        assert len(actions) == 1
        from actions.combat import ApplyPowerAction
        assert isinstance(actions[0], ApplyPowerAction)
        assert actions[0].power == "Regeneration"
        assert actions[0].amount == 25
    
    def test_sundial_gains_energy_on_shuffle(self):
        """Sundial should gain 2 energy every 3 shuffles"""
        from relics.global_relics.uncommon import Sundial
        from player.player import Player
        from actions.combat import GainEnergyAction
        from engine.game_state import GameState
        
        # Mock game state
        from engine.game_state import game_state
        game_state.__init__()  # Reset singleton for test
        player = Player(max_hp=70, max_energy=5)
        game_state.player = player
        
        # Add relic
        sundial = Sundial()
        game_state.player.relics = [sundial]
        
        # Trigger on_shuffle 3 times
        actions = []
        for _ in range(2):
            actions.extend(sundial.on_shuffle())
            assert len(actions) == 0
            assert sundial.shuffle_count == _ + 1
        
        # 3rd shuffle should gain 2 energy (loop ran 2 times, this is the 3rd)
        actions.extend(sundial.on_shuffle())
        
        # Should have 1 action: GainEnergyAction(energy=2)
        # Execute the action
        for action in actions:
            action.execute()
        assert len(actions) == 1
        assert isinstance(actions[0], GainEnergyAction)
        assert actions[0].energy == 2
        assert player.energy == 5  # 3 + 2
    
    def test_relic_hooks_exist(self):
        """New relic hooks should exist in base Relic class"""
        from relics.base import Relic
        
        assert hasattr(Relic, 'on_shuffle')
        assert hasattr(Relic, 'on_use_potion')
        assert hasattr(Relic, 'on_apply_power')


class TestRelicImports:
    """Test that relic modules can be imported."""
    
    def test_common_relics_import(self):
        """Common relics module should import successfully."""
        from relics.global_relics import common
        assert common is not None
        assert hasattr(common, 'Akabeko')
    
    def test_uncommon_relics_import(self):
        """Uncommon relics module should import successfully."""
        from relics.global_relics import uncommon
        assert uncommon is not None
        assert hasattr(uncommon, 'BlueCandle')
    
    def test_rare_relics_import(self):
        """Rare relics module should import successfully."""
        from relics.global_relics import rare
        assert rare is not None
        assert hasattr(rare, 'DeadBranch')
    
    def test_boss_relics_import(self):
        """Boss relics module should import successfully."""
        from relics.global_relics import boss
        assert boss is not None
        assert hasattr(boss, 'SneckoEye')
    
    def test_ironclad_relics_import(self):
        """Ironclad relics module should import successfully."""
        from relics.character import ironclad
        assert ironclad is not None
        assert hasattr(ironclad, 'BurningBlood')


class TestRelicInstantiation:
    """Test that relics can be instantiated."""
    
    def test_common_relics_can_instantiate(self):
        """Common relics should be instantiatable."""
        relic = Akabeko()
        assert relic is not None
    
    def test_uncommon_relics_can_instantiate(self):
        """Uncommon relics should be instantiatable."""
        relic = BlueCandle()
        assert relic is not None
    
    def test_rare_relics_can_instantiate(self):
        """Rare relics should be instantiatable."""
        relic = DeadBranch()
        assert relic is not None
    
    def test_boss_relics_can_instantiate(self):
        """Boss relics should be instantiatable."""
        relic = SneckoEye()
        assert relic is not None
    
    def test_ironclad_relics_can_instantiate(self):
        """Ironclad relics should be instantiatable."""
        relic = IroncladBurningBlood()
        assert relic is not None


class TestRelicMethods:
    """Test that relics have expected methods."""
    
    def test_relic_has_on_combat_start(self):
        """Relics should have on_combat_start hook."""
        relic = Anchor()
        assert hasattr(relic, 'on_combat_start')
    
    def test_relic_has_on_player_turn_start(self):
        """Relics should have on_player_turn_start hook."""
        relic = BronzeScales()
        assert hasattr(relic, 'on_player_turn_start')
    
    def test_relic_has_on_combat_end(self):
        """Relics should have on_combat_end hook."""
        relic = IroncladBurningBlood()
        assert hasattr(relic, 'on_combat_end')
    
    def test_relic_has_on_card_play(self):
        """Relics should have on_card_play hook."""
        relic = DeadBranch()
        assert hasattr(relic, 'on_card_play')

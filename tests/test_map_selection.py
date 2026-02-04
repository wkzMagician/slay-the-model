"""
Test script for map selection functionality.
Tests both human and AI modes.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map.map_manager import MapManager
from ai_tools.map_tools import get_map_context_for_ai
from ai.ai_interface import MockAIDecisionEngine
from engine.game_state import game_state
from config.game_config import GameConfig


def test_map_visualization():
    """Test map visualization for human players"""
    print("="*60)
    print("TEST 1: Map Visualization (Human Mode)")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=12345, act_id=1)
    map_data = map_manager.generate_map()
    
    # Set a starting position
    map_data.set_current_position(0, 1)  # Floor 0, Position 1
    
    # Display the map
    map_manager.display_map_for_human()
    
    # Get available moves
    available_moves = map_manager.get_available_moves()
    print(f"\nAvailable moves: {len(available_moves)}")
    for move in available_moves:
        print(f"  - Floor {move.floor}, Position {move.position}: {move.room_type.value}")
    
    print("\n✓ Map visualization test passed\n")


def test_ai_map_context():
    """Test AI-friendly map context generation"""
    print("="*60)
    print("TEST 2: AI Map Context Generation")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=12345, act_id=1)
    map_data = map_manager.generate_map()
    
    # Set a starting position
    map_data.set_current_position(2, 1)  # Floor 2, Position 1
    
    # Get AI context
    context = get_map_context_for_ai(map_manager)
    
    # Display context structure
    print(f"Current Floor: {context['current_floor']}")
    print(f"Current Position: {context['current_position']}")
    print(f"Available Moves: {len(context['available_moves'])}")
    
    print("\nAvailable Moves Detail:")
    for move in context['available_moves']:
        print(f"  [{move['index']}] Floor {move['floor']}, Pos {move['position']}")
        print(f"      Type: {move['room_type']}, Risk: {move['risk_level']}, Reward: {move['reward_level']}")
    
    print("\nASCII Map:")
    print(context['map_ascii'])
    
    print("\n✓ AI map context test passed\n")


def test_ai_decision_engine():
    """Test AI decision engine with different strategies"""
    print("="*60)
    print("TEST 3: AI Decision Engine")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=12345, act_id=1)
    map_data = map_manager.generate_map()
    
    # Set a starting position
    map_data.set_current_position(0, 1)  # Floor 0, Position 1
    
    # Get AI context
    context = get_map_context_for_ai(map_manager)
    
    # Test different strategies
    strategies = ['first', 'last', 'random', 'least_risk', 'highest_reward']
    
    for strategy in strategies:
        print(f"\nTesting strategy: {strategy}")
        print("-" * 40)
        
        # Create AI engine with this strategy
        ai_engine = MockAIDecisionEngine(strategy=strategy, debug=False)
        
        # Make decision
        choice_index = ai_engine.make_map_decision(context)
        selected_move = context['available_moves'][choice_index]
        
        print(f"Selected: [{choice_index}] Floor {selected_move['floor']}, Pos {selected_move['position']}")
        print(f"  Type: {selected_move['room_type']}, Risk: {selected_move['risk_level']}, Reward: {selected_move['reward_level']}")
    
    print("\n✓ AI decision engine test passed\n")


def test_human_mode_simulation():
    """Simulate human mode map selection"""
    print("="*60)
    print("TEST 4: Human Mode Simulation")
    print("="*60)
    
    # Initialize game state with human mode
    config = GameConfig(mode="human", language="en", seed=12345, debug=True)
    game_state.config = config
    
    # Initialize map
    from map import MapManager
    game_state.map_manager = MapManager(config.seed, act_id=1)
    game_state.map_data = game_state.map_manager.generate_map()
    
    # Set a starting position
    game_state.map_data.set_current_position(0, 1)
    
    # Display map
    game_state.map_manager.display_map_for_human()
    
    # Get available moves
    available_moves = game_state.map_manager.get_available_moves()
    
    print("\nSimulating human selection...")
    print("Available moves:")
    for idx, move in enumerate(available_moves):
        print(f"  [{idx}] Floor {move.floor}, Position {move.position} - {move.room_type.value}")
    
    # Simulate selecting the first option
    selected_index = 0
    selected_move = available_moves[selected_index]
    
    print(f"\nHuman selected: [{selected_index}] Floor {selected_move.floor}, Position {selected_move.position}")
    print(f"  Room Type: {selected_move.room_type.value}")
    
    # Move to the selected node
    new_room = game_state.map_manager.move_to_node(selected_move.floor, selected_move.position)
    print(f"  New room created: {new_room.__class__.__name__}")
    
    print("\n✓ Human mode simulation test passed\n")


def test_ai_mode_simulation():
    """Simulate AI mode map selection"""
    print("="*60)
    print("TEST 5: AI Mode Simulation")
    print("="*60)
    
    # Initialize game state with AI mode
    config = GameConfig(mode="ai", language="en", seed=12345, debug=True, debug=False)
    game_state.config = config
    
    # Initialize map
    from map import MapManager
    game_state.map_manager = MapManager(config.seed, act_id=1)
    game_state.map_data = game_state.map_manager.generate_map()
    
    # Set a starting position
    game_state.map_data.set_current_position(0, 1)
    
    print("Simulating AI selection with 'least_risk' strategy...")
    
    # Create AI engine
    ai_engine = MockAIDecisionEngine(strategy="least_risk", debug=True)
    
    # Get context
    context = get_map_context_for_ai(game_state.map_manager)
    
    # Make decision
    choice_index = ai_engine.make_map_decision(context)
    selected_move = context['available_moves'][choice_index]
    
    print(f"\nAI selected: [{choice_index}] Floor {selected_move['floor']}, Position {selected_move['position']}")
    print(f"  Room Type: {selected_move['room_type']}")
    print(f"  Risk Level: {selected_move['risk_level']}")
    print(f"  Reward Level: {selected_move['reward_level']}")
    
    # Move to the selected node
    new_room = game_state.map_manager.move_to_node(selected_move['floor'], selected_move['position'])
    print(f"  New room created: {new_room.__class__.__name__}")
    
    print("\n✓ AI mode simulation test passed\n")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MAP SELECTION FUNCTIONALITY TESTS")
    print("="*60 + "\n")
    
    try:
        test_map_visualization()
        test_ai_map_context()
        test_ai_decision_engine()
        test_human_mode_simulation()
        test_ai_mode_simulation()
        
        print("="*60)
        print("ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
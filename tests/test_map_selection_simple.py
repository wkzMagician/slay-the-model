"""
Simple test script for map selection functionality.
Avoids circular imports by testing components independently.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from map.map_manager import MapManager


def test_map_visualization():
    """Test map visualization for human players"""
    print("="*60)
    print("TEST 1: Map Visualization (Human Mode)")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=12345, act_id=1)
    map_data = map_manager.generate_map()
    
    # Set a starting position
    map_data.set_current_position(0, 0)  # Floor 0, Position 1
    
    # Display the map
    map_manager.display_map_for_human()
    
    # Get available moves
    available_moves = map_manager.get_available_moves()
    print(f"\nAvailable moves: {len(available_moves)}")
    for move in available_moves:
        print(f"  - Floor {move.floor}, Position {move.position}: {move.room_type.value}")
    
    print("\n[PASS] Map visualization test passed\n")


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
    context = map_manager.get_map_for_ai()
    
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
    
    print("\n[PASS] AI map context test passed\n")


def test_ai_tools():
    """Test AI tools module"""
    print("="*60)
    print("TEST 3: AI Tools Module")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=54321, act_id=1)
    map_data = map_manager.generate_map()
    map_data.set_current_position(1, 0)
    
    # Test get_map_context_for_ai
    from ai_tools.map_tools import get_map_context_for_ai
    context = get_map_context_for_ai(map_manager)
    
    print(f"Context keys: {list(context.keys())}")
    print(f"Has ASCII map: {'map_ascii' in context}")
    print(f"Has JSON map: {'map_json' in context}")
    print(f"Has available moves: {'available_moves' in context}")
    
    # Test format_map_ascii
    from ai_tools.map_tools import format_map_ascii
    ascii_map = format_map_ascii(map_manager)
    print(f"\nASCII map length: {len(ascii_map)} characters")
    print("First 200 chars of ASCII map:")
    print(ascii_map[:200])
    
    # Test format_map_json
    from ai_tools.map_tools import format_map_json
    json_map = format_map_json(map_manager)
    print(f"\nJSON map structure: {json_map['total_floors']} floors")
    
    print("\n[PASS] AI tools test passed\n")


def test_ai_decision_engine():
    """Test AI decision engine with different strategies"""
    print("="*60)
    print("TEST 4: AI Decision Engine")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=99999, act_id=1)
    map_data = map_manager.generate_map()
    map_data.set_current_position(0, 0)
    
    # Get AI context
    context = map_manager.get_map_for_ai()
    
    # Test different strategies
    strategies = ['first', 'last', 'random', 'least_risk', 'highest_reward']
    
    from ai.ai_interface import MockAIDecisionEngine
    
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
    
    print("\n[PASS] AI decision engine test passed\n")


def test_move_to_node():
    """Test moving to different nodes"""
    print("="*60)
    print("TEST 5: Move to Node Functionality")
    print("="*60)
    
    # Create a map manager
    map_manager = MapManager(seed=11111, act_id=1)
    map_data = map_manager.generate_map()
    
    # Start at floor 0, position 0
    map_data.set_current_position(0, 0)
    print(f"Starting at Floor {map_data.current_floor}, Position {map_data.current_position}")
    
    # Get available moves
    available_moves = map_manager.get_available_moves()
    print(f"Available moves: {len(available_moves)}")
    
    # Move to first available node
    if available_moves:
        first_move = available_moves[0]
        print(f"\nMoving to Floor {first_move.floor}, Position {first_move.position}")
        
        new_room = map_manager.move_to_node(first_move.floor, first_move.position)
        print(f"New position: Floor {map_data.current_floor}, Position {map_data.current_position}")
        print(f"Room created: {new_room.__class__.__name__}")
        
        # Verify position changed
        assert map_data.current_floor == first_move.floor
        assert map_data.current_position == first_move.position
        
        print("\n[PASS] Move to node test passed\n")
    else:
        print("No available moves to test\n")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MAP SELECTION FUNCTIONALITY TESTS (SIMPLE)")
    print("="*60 + "\n")
    
    try:
        test_map_visualization()
        test_ai_map_context()
        test_ai_tools()
        test_ai_decision_engine()
        test_move_to_node()
        
        print("="*60)
        print("ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
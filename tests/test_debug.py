#!/usr/bin/env python3
"""Debug script to capture full error traceback."""

import sys
import traceback

try:
    from player.player_factory import create_player, list_characters
    
    print("Testing character system...")
    characters = list_characters()
    print(f"Available characters: {characters}")
    
    player = create_player("Ironclad")
    print(f"Created player: {player.character}")
    print(f"Max HP: {player.max_hp}")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

print("\nSUCCESS!")
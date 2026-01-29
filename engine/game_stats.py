"""
Global game stats containing game mechanics
"""
class GameStats:
    """Global game stats containing all persistent game data"""

    def __init__(self):
        # neo blessing stats
        self.neow_max_hp_small_increases = {
            "Ironclad": 8,
            "Silent": 6,
            "Defect": 7,
            "Watcher": 7
        }
        self.neow_max_hp_small_decreases = {
            "Ironclad": 8,
            "Silent": 7,
            "Defect": 7,
            "Watcher": 7
        }
        self.neow_max_hp_large_increases = {
            "Ironclad": 16,
            "Silent": 12,
            "Defect": 14,
            "Watcher": 14
        }

# Global game state instance
game_stats = GameStats()
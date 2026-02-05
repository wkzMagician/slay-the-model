"""
The Hexaghost - Boss
Final boss. Unique enemy that appears once per game.
"""
from entities.enemy import Enemy


class TheHexaghost(Enemy):
    """The Hexaghost - Final boss that appears once per game"""
    
    def __init__(self):
        super().__init__(
            name="The Hexaghost",
            max_hp=250,
            damage=35,
            is_elite=False,
            is_boss=True
        )

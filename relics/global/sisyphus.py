"""
Sisyphus (斯巴达克斯) - Common relic
At the start of each combat, play the 3 lowest cost cards from your deck.

这是一个非常强大的遗物，因为它可以让你在战斗开始时打出更强大的卡牌。
"""
from relics.base import Relic
from utils.types import RarityType
from utils.registry import register


@register("relic")
class Sisyphus(Relic):
    """斯巴达克斯 - Play the 3 lowest cost cards from deck at combat start"""

    def __init__(self):
        super().__init__()
        self.idstr = "Sisyphus"
        self.name_key = "relics.sisyphus.name"
        self.description_key = "relics.sisyphus.description"
        self.rarity = RarityType.COMMON

    def on_combat_start(self):
        """At the start of combat, play the 3 lowest cost cards from deck"""
        from entities.player import Player
        from actions.card import PlayCardAction

        # Get player from game state
        from engine.game_state import game_state
        player = game_state.player

        if not player or not hasattr(player, 'card_manager'):
            return

        # Get deck
        deck = player.card_manager.get_pile('deck')

        if not deck or len(deck) < 3:
            return

        # Get the 3 lowest cost cards
        # Sort by cost, then by some secondary criteria
        sorted_cards = sorted(deck, key=lambda c: (
            c.get_final_cost(player),
            # Secondary sort by: 
            1. Higher damage if costs equal (attack cards prioritized)
            2. Block amount (skills prioritized)
            3. Uncommon rarity
            # For ties: first by card ID (stable ordering)
        ))[:3]

        # Create play card actions for each of the 3 cards
        play_actions = []
        for card in sorted_cards:
            play_actions.append(PlayCardAction(card=card))

        return play_actions

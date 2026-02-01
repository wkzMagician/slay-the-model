from utils.localizable import Localizable


class Relic(Localizable):
    localization_prefix = "relics"
    rarity = "Common"

    def __init__(self):
        pass

    def on_player_turn_start(self, player, entities):
        """Called at the start of player's turn"""
        pass

    def on_player_turn_end(self, player, entities):
        """Called at the end of player's turn"""
        pass

    def on_enemy_turn_start(self, enemy, player, entities):
        """Called at the start of enemy's turn"""
        pass

    def on_enemy_turn_end(self, enemy, player, entities):
        """Called at the end of enemy's turn"""
        pass

    def on_card_play(self, card, player, entities):
        """Called when a card is played"""
        pass

    def on_damage_dealt(self, damage, target, player, entities) -> int:
        """Called when damage is dealt"""
        return damage

    def on_damage_taken(self, damage, source, player, entities):
        """Called when damage is taken"""
        pass

    def on_heal(self, heal_amount, player, entities):
        """Called when healing occurs"""
        pass

    def on_combat_start(self, player, entities):
        """Called at the start of combat"""
        pass

    def on_combat_end(self, player, entities):
        """Called at the end of combat"""
        pass

    def on_rest_site_enter(self, player, entities):
        """Called when entering a rest site"""
        pass
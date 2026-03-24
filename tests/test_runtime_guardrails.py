import pytest

from entities.creature import Creature
from player.player_factory import create_player


def test_take_damage_rejects_list_input():
    creature = Creature(max_hp=10)

    with pytest.raises(TypeError, match="take_damage expects int"):
        creature.take_damage([3])


def test_create_player_rejects_missing_registered_starter_cards():
    with pytest.raises(ValueError, match="Card not found in registry: silent\\."):
        create_player("Silent")


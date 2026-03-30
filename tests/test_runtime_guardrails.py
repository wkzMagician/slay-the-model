import pytest
from typing import cast

from entities.creature import Creature
from player.player_factory import create_player


def test_take_damage_rejects_list_input():
    creature = Creature(max_hp=10)

    with pytest.raises(TypeError, match="take_damage expects int"):
        creature.take_damage([3])  # pyright: ignore[reportArgumentType]


def test_create_player_builds_silent_successfully():
    player = create_player("Silent")

    assert player.character == "Silent"
    assert player.namespace == "silent"
    assert len(player.card_manager.get_pile("deck")) == 12

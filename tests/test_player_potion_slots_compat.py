from player.player import Player


def test_player_potion_slots_alias_updates_potion_limit():
    player = Player()

    assert player.potion_slots == player.potion_limit == 3

    player.potion_slots += 2

    assert player.potion_slots == 5
    assert player.potion_limit == 5

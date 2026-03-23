from actions.combat import ApplyPowerAction
from engine.game_state import game_state
from player.player import Player
from powers.definitions.constricted import ConstrictedPower


def test_constricted_power_loses_hp_on_turn_end():
    player = Player(max_hp=50)
    player.hp = 40
    power = ConstrictedPower(amount=10, owner=player)
    player.add_power(power)

    for action in power.on_turn_end():
        action.execute()

    assert player.hp == 30


def test_apply_power_action_resolves_constricted_alias():
    game_state.player = Player(max_hp=50)

    ApplyPowerAction('constricted', game_state.player, amount=10, duration=-1).execute()

    power = game_state.player.get_power('Constricted')
    assert power is not None
    assert power.amount == 10

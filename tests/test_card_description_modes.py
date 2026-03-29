from cards.ironclad.bash import Bash
from engine.game_state import game_state
from player.player import Player
from powers.definitions.strength import StrengthPower


def test_card_description_uses_base_values_outside_combat():
    player = Player()
    player.powers = [StrengthPower(amount=3, owner=player)]
    game_state.player = player

    card = Bash()

    assert str(card.description) == "Deal 8 damage. Apply 2 Vulnerable."
    assert str(card.combat_description) == "Deal 11 damage. Apply 2 Vulnerable."

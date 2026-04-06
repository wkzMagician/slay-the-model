from cards.watcher import Vault
from enemies.base import Enemy
from enemies.intention import Intention
from tests.test_combat_utils import create_test_helper


class _TrackingIntention(Intention):
    def execute(self):
        self.enemy.executed.append(self.name)


class _AlternatingEnemy(Enemy):
    def __init__(self):
        super().__init__(hp_range=(40, 40))
        self.executed = []
        self._next = "first"
        self.add_intention(_TrackingIntention("first", self))
        self.add_intention(_TrackingIntention("second", self))

    def determine_next_intention(self, floor: int = 1):
        choice = self.intentions[self._next]
        self._next = "second"
        return choice


def test_vault_skips_enemy_turn_and_preserves_intent_for_next_real_enemy_turn():
    helper = create_test_helper()
    helper.create_player()
    enemy = _AlternatingEnemy()
    combat = helper.start_combat([enemy])

    original_intent = enemy.current_intention.name

    card = Vault()
    helper.add_card_to_hand(card)
    assert helper.play_card(card) is True

    helper.end_player_turn()
    assert enemy.current_intention.name == original_intent

    combat._start_player_turn()
    helper.game_state.drive_actions()
    assert enemy.current_intention.name == original_intent

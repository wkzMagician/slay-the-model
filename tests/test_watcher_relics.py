from actions.watcher import ScryAction
from enemies.act1.cultist import Cultist
from engine.messages import ShuffleMessage
from engine.runtime_api import publish_message
from relics.character.watcher import Melange
from tests.test_combat_utils import create_test_helper
from typing import cast


def test_melange_queues_scry_action_when_shuffle_message_is_published():
    helper = create_test_helper()
    player = helper.create_player()
    player.relics = [Melange()]
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    helper.game_state.action_queue.clear()

    publish_message(ShuffleMessage(owner=player))

    queued = cast(ScryAction, helper.game_state.action_queue.peek_next())
    assert isinstance(queued, ScryAction)
    assert queued.count == 3

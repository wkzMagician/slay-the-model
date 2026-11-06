"""Multi-step flow for the colosseum, dead adventurer, and scrap ooze."""
from engine.random_streams import get_rng, StreamRandom

from typing import cast

from actions.base import LambdaAction
from actions.card import AddRandomCardAction
from actions.combat import LoseHPAction, StartFightAction
from actions.display import InputRequestAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from engine.game_state import game_state
from events.dead_adventurer import DeadAdventurer
from events.scrap_ooze import ScrapOoze
from events.the_colosseum import TheColosseum
from tests.test_combat_utils import create_test_helper


def _requests() -> list[InputRequestAction]:
    return [
        cast(InputRequestAction, action)
        for action in game_state.action_queue.queue
        if isinstance(action, InputRequestAction)
    ]


def _options(event) -> list:
    game_state.action_queue.clear()
    event.trigger()
    return list(_requests()[-1].options)


def _run_lambdas(option) -> None:
    for action in option.actions:
        if isinstance(action, LambdaAction):
            action.execute()


def _search_option(options):
    return next(
        option
        for option in options
        if any(not isinstance(action, LambdaAction) for action in option.actions)
    )


def test_colosseum_fights_slavers_then_offers_victory_or_cowardice():
    helper = create_test_helper()
    helper.create_player()
    event = TheColosseum()
    game_state.action_queue.clear()

    event.trigger()

    assert event.event_ended is False
    requests = _requests()
    assert len(requests) == 1
    assert len(requests[0].options) == 1
    opening = requests[0].options[0]
    fight = next(action for action in opening.actions if isinstance(action, StartFightAction))
    fight = cast(StartFightAction, fight)
    assert [type(enemy).__name__ for enemy in fight.enemies] == ["BlueSlaver", "RedSlaver"]

    for action in fight.victory_actions:
        action.execute()

    assert event.first_fight_done is True
    assert event.event_ended is False
    options = list(_requests()[-1].options)
    victory = next(
        option
        for option in options
        if any(isinstance(action, StartFightAction) for action in option.actions)
    )
    second = next(action for action in victory.actions if isinstance(action, StartFightAction))
    assert [type(enemy).__name__ for enemy in second.enemies] == ["Taskmaster", "GremlinNob"]
    rewards = second.victory_actions
    assert any(isinstance(action, AddGoldAction) and action.amount == 100 for action in rewards)
    assert any(isinstance(action, AddRandomCardAction) for action in rewards)
    relics = [action for action in rewards if isinstance(action, AddRandomRelicAction)]
    assert [relic.rarities for relic in relics] == [["rare"], ["uncommon"]]

    cowardice = next(option for option in options if option is not victory)
    _run_lambdas(cowardice)
    assert event.event_ended is True


def test_dead_adventurer_rolls_the_current_search_and_counts_it_afterward(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 0
    rolls = iter([100, 26, 51])
    monkeypatch.setattr(get_rng("misc"), "choice", lambda seq: seq[0])
    monkeypatch.setattr(get_rng("misc"), "randint", lambda a, b: next(rolls))

    event = DeadAdventurer()
    options = _options(event)

    assert event.search_count == 0
    assert not any(
        isinstance(action, StartFightAction)
        for action in _search_option(options).actions
    )

    _run_lambdas(_search_option(options))
    assert event.search_count == 1
    assert not any(
        isinstance(action, StartFightAction)
        for action in _search_option(list(_requests()[-1].options)).actions
    )

    _run_lambdas(_search_option(list(_requests()[-1].options)))
    assert event.search_count == 2
    assert not any(
        isinstance(action, StartFightAction)
        for action in _search_option(list(_requests()[-1].options)).actions
    )

    _run_lambdas(_search_option(list(_requests()[-1].options)))
    assert event.search_count == 3
    assert event.event_ended is False
    final_options = list(_requests()[-1].options)
    assert all(
        all(isinstance(action, LambdaAction) for action in option.actions)
        for option in final_options
    )


def test_dead_adventurer_ascension_15_first_search_uses_ten_percent(monkeypatch):
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 15
    monkeypatch.setattr(get_rng("misc"), "choice", lambda seq: seq[0])
    monkeypatch.setattr(get_rng("misc"), "randint", lambda a, b: 11)

    event = DeadAdventurer()
    options = _options(event)

    assert event.search_count == 0
    assert not any(
        isinstance(action, StartFightAction)
        for action in _search_option(options).actions
    )


def test_scrap_ooze_loses_hp_and_then_rolls(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = 0
    monkeypatch.setattr(get_rng("misc"), "random", lambda: 0.0)

    event = ScrapOoze()
    options = _options(event)

    assert event.attempt_count == 0
    assert event.relic_obtained is False
    assert event.event_ended is False
    reach = next(
        option
        for option in options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    hp_loss = next(action for action in reach.actions if isinstance(action, LoseHPAction))
    assert hp_loss.amount == 3
    assert not any(isinstance(action, AddRandomRelicAction) for action in reach.actions)

    for action in reach.actions:
        action.execute()

    assert player.hp == player.max_hp - 3
    assert event.relic_obtained is True
    assert event.attempt_count == 0
    queue = game_state.action_queue.queue
    relic_index = next(
        index
        for index, action in enumerate(queue)
        if isinstance(action, AddRandomRelicAction)
    )
    end = queue[relic_index + 1]
    assert isinstance(end, LambdaAction)
    end.execute()
    assert event.event_ended is True


def test_scrap_ooze_can_reach_again_after_a_failure(monkeypatch):
    helper = create_test_helper()
    player = helper.create_player()
    game_state.ascension = 15
    monkeypatch.setattr(get_rng("misc"), "random", lambda: 0.99)

    event = ScrapOoze()
    options = _options(event)
    reach = next(
        option
        for option in options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert next(action.amount for action in reach.actions if isinstance(action, LoseHPAction)) == 5
    assert event.event_ended is False

    for action in reach.actions:
        action.execute()

    assert player.hp == player.max_hp - 5
    assert event.attempt_count == 1
    assert event.relic_obtained is False
    assert event.event_ended is False
    again = next(
        option
        for option in _requests()[-1].options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert next(action.amount for action in again.actions if isinstance(action, LoseHPAction)) == 6

    leave = next(
        option
        for option in _requests()[-1].options
        if all(isinstance(action, LambdaAction) for action in option.actions)
    )
    _run_lambdas(leave)
    assert event.event_ended is True

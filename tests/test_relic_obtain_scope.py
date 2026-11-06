"""REL-011: pickup hooks belong to the acquired instance, observers broadcast."""
import random

import pytest

from actions.reward import AddRandomRelicAction, AddRelicAction, AddRelicByNameAction
from engine.message_bus import MessageBus
from engine.message_contracts import invoke_subscription_contract
from engine.messages import RelicObtainedMessage
from engine.subscriptions import subscribe
from player.player_factory import create_player
from relics.base import Relic
from relics.global_relics.boss import CallingBell
from relics.global_relics.common import Anchor, PotionBelt, Strawberry
from relics.global_relics.rare import Mango, OldCoin
from relics.global_relics.uncommon import Pear
from tests.test_combat_utils import create_test_helper


def environment():
    helper = create_test_helper()
    helper.create_player()
    random.seed(829)
    return helper.game_state


class CountingRelic(Relic):
    def __init__(self):
        super().__init__()
        self.pickups = 0
        self.observed = 0

    # Intentionally inherit the base on_obtain subscription metadata.
    def on_obtain(self):
        self.pickups += 1

    @subscribe(RelicObtainedMessage)
    def observe_any_pickup(self):
        self.observed += 1


def test_two_same_class_instances_pick_up_once_but_observe_both_messages():
    gs = environment()
    old, new = CountingRelic(), CountingRelic()
    AddRelicAction(old).execute()
    gs.drive_actions()
    AddRelicAction(new).execute()
    gs.drive_actions()
    assert (old.pickups, new.pickups) == (1, 1)
    assert (old.observed, new.observed) == (2, 1)


def test_direct_contract_invocation_filters_old_instance_only():
    gs = environment()
    old, new = CountingRelic(), CountingRelic()
    message = RelicObtainedMessage(owner=gs.player, relic=new)
    invoke_subscription_contract(old.on_obtain, message)
    invoke_subscription_contract(new.on_obtain, message)
    invoke_subscription_contract(old.observe_any_pickup, message)
    assert (old.pickups, new.pickups, old.observed) == (0, 1, 1)


def test_explicit_bus_participants_keep_generic_handlers_and_observers():
    gs = environment()
    old, new = CountingRelic(), CountingRelic()
    class Observer:
        priority = 0
        def __init__(self):
            self.messages = []
        def handles(self, message):
            return isinstance(message, RelicObtainedMessage)
        def handle(self, message):
            self.messages.append(message)
            return []
    observer = Observer()
    bus = MessageBus()
    bus.register(observer)
    message = RelicObtainedMessage(owner=gs.player, relic=new)
    bus.publish(message, participants=[old, new])
    assert observer.messages == [message]
    assert (old.pickups, new.pickups) == (0, 1)
    assert (old.observed, new.observed) == (1, 1)


@pytest.mark.parametrize('factory,field,delta', [
    (PotionBelt, 'potion_limit', 2), (OldCoin, 'gold', 300),
    (Strawberry, 'max_hp', 7), (Pear, 'max_hp', 10), (Mango, 'max_hp', 14),
])
def test_real_pickup_rewards_do_not_repeat_when_anchor_is_acquired(factory, field, delta):
    gs = environment()
    initial = getattr(gs.player, field)
    AddRelicAction(factory()).execute()
    gs.drive_actions()
    assert getattr(gs.player, field) == initial + delta
    AddRelicAction(Anchor()).execute()
    gs.drive_actions()
    assert getattr(gs.player, field) == initial + delta


@pytest.mark.parametrize('entry', ['instance', 'name', 'random'])
def test_reward_entry_points_do_not_repeat_old_pickup(entry):
    gs = environment()
    old = CountingRelic()
    AddRelicAction(old).execute()
    gs.drive_actions()
    action = {'instance': lambda: AddRelicAction(Anchor()),
              'name': lambda: AddRelicByNameAction('Anchor'),
              'random': lambda: AddRandomRelicAction()}[entry]()
    action.execute()
    gs.drive_actions()
    assert len(gs.player.relics) == 2
    assert old.pickups == 1
    assert old.observed == 2


@pytest.mark.parametrize('character', ['Ironclad', 'Silent', 'Defect', 'Watcher'])
def test_native_calling_bell_chain_terminates_with_one_curse_and_three_relics(character):
    gs = environment()
    gs.player = create_player(character)
    initial_relics = len(gs.player.relics)
    AddRelicAction(CallingBell()).execute()
    gs.drive_actions()
    assert gs.action_queue.is_empty()
    assert len(gs.player.relics) == initial_relics + 4
    assert sum(type(c).__name__ == 'CurseOfTheBell'
               for c in gs.player.card_manager.get_pile('deck')) == 1
    assert sum(isinstance(r, CallingBell) for r in gs.player.relics) == 1


def test_shop_purchase_keeps_old_pickup_hook_inactive(monkeypatch):
    from rooms.shop import ShopRoom, ShopItem
    gs = environment()
    old = CountingRelic()
    AddRelicAction(old).execute()
    gs.drive_actions()
    # Component shop inventory fixture; native menu, payment and acquisition.
    room = ShopRoom()
    item = ShopItem('relic', Anchor(), 10)
    room.items = [item]
    gs.current_room = room
    calls = []
    def choose(request):
        calls.append(True)
        wanted = 'BuyItemAction' if len(calls) == 1 else 'LeaveRoomAction'
        return [next(i for i, option in enumerate(request.options)
                     if any(type(action).__name__ == wanted for action in option.actions)
                     and (wanted != 'BuyItemAction' or any(getattr(action, 'item_idx', -1) == 0
                                                          for action in option.actions)))]
    monkeypatch.setattr(gs, '_resolve_debug_selection', choose)
    gs.config.auto_select = False
    initial = gs.player.gold
    room.enter()
    gs.drive_actions()
    assert item.purchased and room.should_leave
    assert gs.player.gold == initial - 10
    assert (old.pickups, old.observed) == (1, 2)
    assert any(isinstance(r, Anchor) for r in gs.player.relics)


@pytest.mark.parametrize('boss', [False, True])
def test_chest_menu_acquisition_keeps_old_pickup_hook_inactive(boss):
    from rooms.treasure import TreasureRoom
    gs = environment()
    old = CountingRelic()
    AddRelicAction(old).execute()
    gs.drive_actions()
    room = TreasureRoom(is_boss=boss)
    gs.current_room = room
    # Pin the component's boss pool, not the effects or reward callback.
    if boss:
        gs.boss_relic_pool.remaining = ['BlackStar', 'Sozu', 'RunicDome']
    room.init()
    room.enter()
    gs.drive_actions()
    assert room.chest_opened and room.should_leave
    assert len(gs.player.relics) == 2
    assert (old.pickups, old.observed) == (1, 2)

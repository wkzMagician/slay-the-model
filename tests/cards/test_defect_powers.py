from actions.base import LambdaAction
from actions.combat import ApplyPowerAction
from actions.combat_damage import DealDamageAction
from cards.base import Card
from cards.defect.white_noise import WhiteNoise
from cards.defect.beam_cell import BeamCell
from cards.defect.strike import Strike
from cards.defect.zap import Zap
from enemies.base import Enemy
from engine.runtime_api import add_action
from orbs.base import Orb
from orbs.lightning import LightningOrb
from powers.definitions.focus import FocusPower
from tests.test_combat_utils import create_test_helper
from utils.registry import register
from utils.types import CardType, RarityType

from cards.defect.amplify import Amplify
from cards.defect.biased_cognition import BiasedCognition
from cards.defect.buffer import Buffer
from cards.defect.capacitor import Capacitor
from cards.defect.creative_ai import CreativeAI
from cards.defect.defragment import Defragment
from cards.defect.echo_form import EchoForm
from cards.defect.electrodynamics import Electrodynamics
from cards.defect.hello_world import HelloWorld
from cards.defect.loop import Loop
from cards.defect.machine_learning import MachineLearning
from cards.defect.self_repair import SelfRepair
from cards.defect.static_discharge import StaticDischarge
from cards.defect.storm import Storm
from powers.definitions.lock_on import LockOnPower


class _NoOpEnemy(Enemy):
    def __init__(self, hp: int = 40):
        super().__init__(max_hp=hp, name="Target Dummy")

    def determine_next_intention(self, floor: int = 1):
        class _Intent:
            name = "Idle"
            description = "Idle"

            def execute(self):
                return None

        return _Intent()


class _TrackingOrb(Orb):
    def __init__(self):
        super().__init__()
        self.passive_count = 0

    def on_passive(self) -> None:
        add_action(LambdaAction(func=self._mark))

    def on_evoke(self) -> None:
        return None

    def _mark(self):
        self.passive_count += 1


@register("card")
class _TestPowerCard(Card):
    card_type = CardType.POWER
    rarity = RarityType.SPECIAL
    base_cost = 1

    def on_play(self, targets=[]):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        add_action(ApplyPowerAction(FocusPower(amount=1, owner=game_state.player), game_state.player))


class TestDefectPowers:
    def setup_method(self):
        self.helper = create_test_helper()
        self.player = self.helper.create_player(hp=75, max_hp=75, energy=3)
        self.player.namespace = "defect"
        self.player.base_orb_slots = 3
        self.player.orb_manager.max_orb_slots = 3

    def test_defragment_applies_focus(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Defragment()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        focus = self.player.get_power("Focus")
        assert focus is not None
        assert focus.amount == 1

    def test_capacitor_increases_orb_slots(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Capacitor()
        self.helper.add_card_to_hand(card)

        assert self.player.orb_manager.max_orb_slots == 3
        assert self.helper.play_card(card) is True
        assert self.player.orb_manager.max_orb_slots == 5

    def test_loop_triggers_leftmost_orb_additional_time(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        orb = _TrackingOrb()
        self.player.orb_manager.add_orb(orb)
        card = Loop()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        assert orb.passive_count == 1

    def test_storm_channels_lightning_on_power_play(self):
        self.helper.start_combat([_NoOpEnemy()])
        storm = Storm()
        proc = Defragment()
        self.helper.add_card_to_hand(storm)
        self.helper.add_card_to_hand(proc)

        assert self.helper.play_card(storm) is True
        before = len(self.player.orb_manager.orbs)
        assert self.helper.play_card(proc) is True

        assert len(self.player.orb_manager.orbs) == before + 1
        assert isinstance(self.player.orb_manager.orbs[-1], LightningOrb)

    def test_static_discharge_channels_lightning_on_attack_damage(self):
        enemy = _NoOpEnemy()
        self.helper.start_combat([enemy])
        card = StaticDischarge()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        add_action(DealDamageAction(damage=3, target=self.player, source=enemy, damage_type="attack"))
        self.helper.game_state.drive_actions()

        assert len(self.player.orb_manager.orbs) == 1
        assert isinstance(self.player.orb_manager.orbs[0], LightningOrb)

    def test_machine_learning_draws_at_turn_start(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = MachineLearning()
        self.helper.add_card_to_hand(card)
        self.helper.add_card_to_draw_pile(Zap())

        assert self.helper.play_card(card) is True
        hand_before = len(self.player.card_manager.get_pile("hand"))
        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        assert len(self.player.card_manager.get_pile("hand")) >= hand_before + 1

    def test_hello_world_adds_random_common_defect_card(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = HelloWorld()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        hand_before = len(self.player.card_manager.get_pile("hand"))
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        hand_after = self.player.card_manager.get_pile("hand")

        assert len(hand_after) >= hand_before + 1
        assert any(c.namespace == "defect" and c.rarity == RarityType.COMMON for c in hand_after)

    def test_creative_ai_adds_random_power_card(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = CreativeAI()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        hand_before = len(self.player.card_manager.get_pile("hand"))
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        hand_after = self.player.card_manager.get_pile("hand")

        assert len(hand_after) >= hand_before + 1
        assert any(c.namespace == "defect" and c.card_type == CardType.POWER for c in hand_after)

    def test_creative_ai_never_generates_self_repair(self, monkeypatch):
        from cards.defect.buffer import Buffer
        from cards.defect.self_repair import SelfRepair
        import actions.card_transform as card_transform_module

        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = CreativeAI()
        self.helper.add_card_to_hand(card)

        def fake_random_card(*args, **kwargs):
            excluded = set(kwargs.get("exclude_card_ids") or [])
            if "defect.SelfRepair" in excluded:
                return Buffer()
            return SelfRepair()

        monkeypatch.setattr(card_transform_module, "get_random_card", fake_random_card)

        assert self.helper.play_card(card) is True
        combat._start_player_turn()
        self.helper.game_state.drive_actions()
        hand = self.player.card_manager.get_pile("hand")
        assert not any(isinstance(card_in_hand, SelfRepair) for card_in_hand in hand)

    def test_biased_cognition_loses_focus_each_turn(self):
        self.helper.start_combat([_NoOpEnemy()])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        card = BiasedCognition()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        focus = self.player.get_power("Focus")
        assert focus is not None
        assert focus.amount == 4
        assert self.player.get_power("Biased Cognition") is not None

        combat._start_player_turn()
        self.helper.game_state.drive_actions()

        focus = self.player.get_power("Focus")
        assert focus is not None
        assert focus.amount == 3

    def test_self_repair_heals_at_combat_end(self):
        enemy = _NoOpEnemy(hp=1)
        self.helper.start_combat([enemy])
        combat = self.helper.game_state.current_combat
        assert combat is not None
        self.player.hp = 50
        card = SelfRepair()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        enemy.hp = 0
        result = combat._check_combat_end()

        assert result is not None
        assert self.player.hp == 57

    def test_echo_form_duplicates_first_card_each_turn(self):
        enemy = _NoOpEnemy(hp=20)
        self.helper.start_combat([enemy])
        echo = EchoForm()
        beam = BeamCell()
        self.helper.add_card_to_hand(echo)
        self.helper.add_card_to_hand(beam)

        assert self.helper.play_card(echo) is True
        assert self.helper.play_card(beam, enemy) is True

        assert enemy.hp == 13

    def test_amplify_duplicates_next_power_card(self):
        self.helper.start_combat([_NoOpEnemy()])
        amplify = Amplify()
        defragment = Defragment()
        self.helper.add_card_to_hand(amplify)
        self.helper.add_card_to_hand(defragment)

        assert self.helper.play_card(amplify) is True
        assert self.helper.play_card(defragment) is True

        focus = self.player.get_power("Focus")
        assert focus is not None
        assert focus.amount == 2

    def test_electrodynamics_makes_lightning_hit_all_enemies(self):
        enemy_a = _NoOpEnemy(hp=20)
        enemy_b = _NoOpEnemy(hp=20)
        self.helper.start_combat([enemy_a, enemy_b])
        card = Electrodynamics()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        assert self.player.get_power("Electro") is not None
        assert len(self.player.orb_manager.orbs) == 2

        self.player.orb_manager.orbs[0].on_passive()
        self.helper.game_state.drive_actions()

        assert enemy_a.hp < 20
        assert enemy_b.hp < 20

    def test_lock_on_removed_by_attack_damage(self):
        enemy = _NoOpEnemy(hp=20)
        self.helper.start_combat([enemy])
        enemy.add_power(LockOnPower(duration=3, owner=enemy))
        strike = Strike()
        self.helper.add_card_to_hand(strike)

        assert self.helper.play_card(strike, enemy) is True
        lock_on = enemy.get_power("Lock-On")
        assert lock_on is not None
        assert lock_on.duration == 3

    def test_white_noise_never_generates_self_repair(self, monkeypatch):
        from cards.defect.self_repair import SelfRepair
        from cards.defect.buffer import Buffer
        import actions.card_transform as card_transform_module

        self.helper.start_combat([_NoOpEnemy()])
        card = WhiteNoise()
        self.helper.add_card_to_hand(card)

        def fake_random_card(*args, **kwargs):
            excluded = set(kwargs.get("exclude_card_ids") or [])
            if "defect.SelfRepair" in excluded:
                return Buffer()
            return SelfRepair()

        monkeypatch.setattr(card_transform_module, "get_random_card", fake_random_card)
        assert self.helper.play_card(card) is True
        hand = self.player.card_manager.get_pile("hand")
        assert not any(isinstance(card_in_hand, SelfRepair) for card_in_hand in hand)

    def test_buffer_card_applies_buffer_power(self):
        self.helper.start_combat([_NoOpEnemy()])
        card = Buffer()
        self.helper.add_card_to_hand(card)

        assert self.helper.play_card(card) is True
        buffer = self.player.get_power("Buffer")
        assert buffer is not None
        assert buffer.amount == 1

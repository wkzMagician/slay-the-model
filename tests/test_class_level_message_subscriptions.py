from actions.combat import GainBlockAction
from cards.base import Card
from enemies.act1.cultist import Cultist
from enemies.act1.lagavulin import Lagavulin
from enemies.act2.the_champ import TheChamp
from enemies.base import Enemy
from engine.messages import (
    AttackPerformedMessage,
    BlockGainedMessage,
    CardAddedToPileMessage,
    CardPlayedMessage,
    CardDiscardedMessage,
    CardDrawnMessage,
    CombatEndedMessage,
    CombatStartedMessage,
    CreatureDiedMessage,
    DamageResolvedMessage,
    GoldGainedMessage,
    HealedMessage,
    HpLostMessage,
    PlayerTurnEndedMessage,
    PlayerTurnStartedMessage,
    PotionUsedMessage,
    PowerAppliedMessage,
    ShuffleMessage,
)
from potions.global_potions import BlockPotion
from engine.message_bus import MessageBus
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power
from player.player import Player
from relics.base import Relic
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType
from entities.creature import Creature


class _CombatStartRelic(Relic):
    def __init__(self):
        super().__init__()
        self.triggered = False

    @subscribe(CombatStartedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_combat_start(self, player, entities):
        self.triggered = True
        return [GainBlockAction(block=3, target=player)]


class _TurnStartPower(Power):
    name = "TestTurnStartPower"

    def __init__(self, amount=0, duration=-1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.triggered = False

    @subscribe(PlayerTurnStartedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_turn_start(self):
        self.triggered = True
        return [GainBlockAction(block=2, target=self.owner)]


class _EnemyTurnStart(Enemy):
    def __init__(self):
        super().__init__(hp_range=(20, 20))
        self.started = False
        self.turn_started = False

    @subscribe(CombatStartedMessage, priority=MessagePriority.ENEMY)
    def on_combat_start(self, floor: int = 1):
        self.started = True

    @subscribe(PlayerTurnStartedMessage, priority=MessagePriority.ENEMY)
    def on_player_turn_start(self):
        self.turn_started = True


class _TurnEndRelic(Relic):
    def __init__(self):
        super().__init__()
        self.turn_ended = False
        self.combat_ended = False

    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_player_turn_end(self, player, entities):
        self.turn_ended = True
        return [GainBlockAction(block=4, target=player)]

    @subscribe(CombatEndedMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_combat_end(self, player, entities):
        self.combat_ended = True
        return [GainBlockAction(block=1, target=player)]


class _TurnEndPower(Power):
    name = "TestTurnEndPower"

    def __init__(self, amount=0, duration=-1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self.turn_ended = False
        self.combat_ended = False

    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_turn_end(self):
        self.turn_ended = True
        return [GainBlockAction(block=5, target=self.owner)]

    @subscribe(CombatEndedMessage, priority=MessagePriority.PLAYER_POWER)
    def on_combat_end(self, owner, entities):
        self.combat_ended = True
        return [GainBlockAction(block=2, target=owner)]


class _TurnEndCard(Card):
    def __init__(self):
        super().__init__()
        self.turn_ended = False

    @subscribe(PlayerTurnEndedMessage, priority=MessagePriority.CARD)
    def on_player_turn_end(self):
        self.turn_ended = True
        return []


class _EconomyRelic(Relic):
    def __init__(self):
        super().__init__()
        self.gold_triggered = False
        self.shuffle_triggered = False
        self.potion_triggered = False

    def on_gold_gained(self, gold_amount: int, player):
        self.gold_triggered = True
        return [GainBlockAction(block=1, target=player)]

    def on_shuffle(self):
        from engine.game_state import game_state

        self.shuffle_triggered = True
        return [GainBlockAction(block=2, target=game_state.player)]

    def on_use_potion(self, potion, player, entities):
        self.potion_triggered = True
        return [GainBlockAction(block=3, target=player)]


class _LifecycleCard(Card):
    def __init__(self):
        super().__init__()
        self.draw_triggered = False
        self.discard_triggered = False

    def on_draw(self):
        self.draw_triggered = True
        return []

    def on_discard(self):
        self.discard_triggered = True
        return []


class _LifecyclePower(Power):
    name = "LifecyclePower"

    def __init__(self, owner=None):
        super().__init__(amount=1, owner=owner)
        self.draw_triggered = False
        self.discard_triggered = False

    def on_card_draw(self, card):
        self.draw_triggered = True
        return [GainBlockAction(block=4, target=self.owner)]

    def on_discard(self, card):
        self.discard_triggered = True
        return [GainBlockAction(block=5, target=self.owner)]


class _LifecycleRelic(Relic):
    def __init__(self):
        super().__init__()
        self.draw_triggered = False
        self.discard_triggered = False
        self.added_triggered = False
        self._target_player: Player | None = None

    def on_card_draw(self, card, player, entities):
        self.draw_triggered = True
        return [GainBlockAction(block=6, target=player)]

    def on_card_discard(self, card, player, entities):
        self.discard_triggered = True
        return [GainBlockAction(block=7, target=player)]

    def on_card_added(self, card, dest_pile="deck"):
        self.added_triggered = True
        return [GainBlockAction(block=8, target=self._target_player)]


class _MessageFormRelic(Relic):
    def __init__(self):
        super().__init__()
        self.seen_message = None

    @subscribe(CardDrawnMessage, priority=MessagePriority.PLAYER_RELIC)
    def on_card_draw_message(self, message):
        self.seen_message = message
        return []


class _ReactionCreature(Creature):
    def __init__(self):
        super().__init__(max_hp=20)
        self.damage_taken_triggered = False
        self.damage_dealt_triggered = False
        self.heal_triggered = False
        self.block_triggered = False
        self.power_added_triggered = False
        self.hp_lost_triggered = False
        self.death_triggered = False

    def on_damage_taken(self, damage, source=None, card=None, damage_type=None):
        self.damage_taken_triggered = True
        return []

    def on_damage_dealt(self, damage, target=None, card=None, damage_type: str = "direct"):
        self.damage_dealt_triggered = True
        return []

    def on_heal(self, amount: int):
        self.heal_triggered = True
        return []

    def on_gain_block(self, amount: int, source=None, card=None):
        self.block_triggered = True
        return []

    def on_power_added(self, power):
        self.power_added_triggered = True
        return []

    def on_lose_hp(self, amount: int, source=None, card=None):
        self.hp_lost_triggered = True
        return []

    def on_death(self):
        self.death_triggered = True
        return []


class _ReactionPower(Power):
    name = "ReactionPower"

    def __init__(self, owner=None):
        super().__init__(amount=1, owner=owner)
        self.damage_taken_triggered = False
        self.block_triggered = False
        self.power_added_triggered = False
        self.hp_lost_triggered = False

    def on_damage_taken(self, damage, source=None, card=None, player=None, damage_type="direct"):
        self.damage_taken_triggered = True
        return []

    def on_gain_block(self, amount: int, player=None, source=None, card=None):
        self.block_triggered = True
        return []

    def on_power_added(self, power, source=None):
        self.power_added_triggered = True
        return []

    def on_lose_hp(self, amount: int, source=None, card=None):
        self.hp_lost_triggered = True
        return []


class _ReactionRelic(Relic):
    def __init__(self):
        super().__init__()
        self.damage_dealt_triggered = False
        self.damage_taken_triggered = False
        self.heal_triggered = False
        self.power_added_triggered = False

    def on_damage_dealt(self, damage, target, player, entities):
        self.damage_dealt_triggered = True
        return []

    def on_damage_taken(self, damage, source, player, entities):
        self.damage_taken_triggered = True
        return []

    def on_heal(self, heal_amount, player, entities):
        self.heal_triggered = True
        return []

    def on_apply_power(self, power, target, player, entities):
        self.power_added_triggered = True
        return []


class _ReactionCard(Card):
    def __init__(self):
        super().__init__()
        self.damage_dealt_triggered = False
        self.fatal_triggered = False

    def on_damage_dealt(self, damage, target=None, card=None, damage_type: str = "direct"):
        self.damage_dealt_triggered = True
        return []

    def on_fatal(self, damage, target=None, card=None, damage_type: str = "direct"):
        self.fatal_triggered = True
        return []


class _PlayAttackPower(Power):
    name = "PlayAttackPower"

    def __init__(self, owner=None):
        super().__init__(amount=1, owner=owner)
        self.card_play_triggered = False
        self.attack_triggered = False

    def on_card_play(self, card, player, targets):
        self.card_play_triggered = True
        return [GainBlockAction(block=9, target=player)]

    def on_attack(self, target=None, source=None, card=None):
        self.attack_triggered = True
        return [GainBlockAction(block=10, target=source)]


class _PlayAttackRelic(Relic):
    def __init__(self):
        super().__init__()
        self.card_play_triggered = False

    def on_card_play(self, card, player, targets):
        self.card_play_triggered = True
        return [GainBlockAction(block=11, target=player)]


class _PlayReactiveCard(Card):
    def __init__(self):
        super().__init__()
        self.card_play_triggered = False

    def on_card_play(self, card, player, targets):
        self.card_play_triggered = True
        return [GainBlockAction(block=12, target=player)]


def test_message_bus_dispatches_decorated_combat_start_subscribers():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _CombatStartRelic()
    player.relics = [relic]
    enemy = _EnemyTurnStart()

    bus = MessageBus()
    actions = bus.publish(
        CombatStartedMessage(owner=player, enemies=[enemy], floor=1),
        participants=[relic, enemy],
    )

    assert relic.triggered is True
    assert enemy.started is True
    assert len(actions) == 1
    assert isinstance(actions[0], GainBlockAction)


def test_start_player_turn_uses_class_level_subscriptions():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = _EnemyTurnStart()
    combat = helper.start_combat([enemy])
    power = _TurnStartPower(owner=player)
    player.add_power(power)

    combat._start_player_turn()
    helper.game_state.drive_actions()

    assert power.triggered is True
    assert enemy.turn_started is True
    assert player.block == 2


def test_message_bus_dispatches_decorated_end_subscribers():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = _EnemyTurnStart()
    relic = _TurnEndRelic()
    power = _TurnEndPower(owner=player)
    card = _TurnEndCard()

    bus = MessageBus()
    turn_end_actions = bus.publish(
        PlayerTurnEndedMessage(owner=player, enemies=[enemy], hand_cards=[card]),
        participants=[relic, power, card],
    )
    combat_end_actions = bus.publish(
        CombatEndedMessage(owner=player, enemies=[enemy]),
        participants=[relic, power],
    )

    assert relic.turn_ended is True
    assert relic.combat_ended is True
    assert power.turn_ended is True
    assert power.combat_ended is True
    assert card.turn_ended is True
    assert [type(action).__name__ for action in turn_end_actions] == ["GainBlockAction", "GainBlockAction"]
    assert [type(action).__name__ for action in combat_end_actions] == ["GainBlockAction", "GainBlockAction"]


def test_end_messages_use_class_level_subscriptions():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=10)
    combat = helper.start_combat([enemy])

    relic = _TurnEndRelic()
    power = _TurnEndPower(owner=player)
    card = _TurnEndCard()
    player.relics = [relic]
    player.add_power(power)
    player.card_manager.add_to_pile(card, "hand", PilePosType.TOP)

    combat._end_player_phase()
    helper.game_state.drive_actions()

    assert relic.turn_ended is True
    assert power.turn_ended is True
    assert card.turn_ended is True
    assert player.block == 9

    enemy.hp = 0
    combat._check_combat_end()

    assert relic.combat_ended is True
    assert power.combat_ended is True
    assert player.block == 12


def test_low_risk_messages_use_relic_base_subscription_metadata():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    relic = _EconomyRelic()
    potion = BlockPotion()

    bus = MessageBus()
    gold_actions = bus.publish(GoldGainedMessage(owner=player, amount=12), participants=[relic])
    shuffle_actions = bus.publish(ShuffleMessage(owner=player), participants=[relic])
    potion_actions = bus.publish(
        PotionUsedMessage(potion=potion, owner=player, targets=[player], entities=[]),
        participants=[relic],
    )

    assert relic.gold_triggered is True
    assert relic.shuffle_triggered is True
    assert relic.potion_triggered is True
    assert [type(action).__name__ for action in gold_actions] == ["GainBlockAction"]
    assert [type(action).__name__ for action in shuffle_actions] == ["GainBlockAction"]
    assert [type(action).__name__ for action in potion_actions] == ["GainBlockAction"]


def test_medium_risk_messages_use_class_level_subscription_metadata():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    card = _LifecycleCard()
    power = _LifecyclePower(owner=player)
    relic = _LifecycleRelic()
    relic._target_player = player
    player.powers = [power]
    player.relics = [relic]

    bus = MessageBus()
    participants = [card, power, relic]

    draw_actions = bus.publish(
        CardDrawnMessage(card=card, owner=player),
        participants=participants,
    )
    discard_actions = bus.publish(
        CardDiscardedMessage(card=card, owner=player, source_pile="hand"),
        participants=participants,
    )
    added_actions = bus.publish(
        CardAddedToPileMessage(card=card, owner=player, dest_pile="deck", source="reward"),
        participants=participants,
    )

    assert card.draw_triggered is True
    assert card.discard_triggered is True
    assert power.draw_triggered is True
    assert power.discard_triggered is True
    assert relic.draw_triggered is True
    assert relic.discard_triggered is True
    assert relic.added_triggered is True
    assert [type(action).__name__ for action in draw_actions] == ["GainBlockAction", "GainBlockAction"]
    assert [type(action).__name__ for action in discard_actions] == ["GainBlockAction", "GainBlockAction"]
    assert [type(action).__name__ for action in added_actions] == ["GainBlockAction"]


def test_card_drawn_message_contract_supports_message_form_dispatch():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    card = _LifecycleCard()
    relic = _MessageFormRelic()
    message = CardDrawnMessage(card=card, owner=player)

    bus = MessageBus()
    actions = bus.publish(message, participants=[relic])

    assert relic.seen_message is message
    assert actions == []


def test_high_risk_messages_use_class_level_subscription_metadata():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    target = _ReactionCreature()
    source = _ReactionCreature()
    power = _ReactionPower(owner=target)
    target.powers = [power]
    relic = _ReactionRelic()
    card = _ReactionCard()
    player.relics = [relic]
    target.hp = 0

    bus = MessageBus()

    damage_actions = bus.publish(
        DamageResolvedMessage(amount=9, target=target, source=source, card=card, damage_type="attack"),
        participants=[power, target, source, card, relic],
    )
    heal_actions = bus.publish(
        HealedMessage(target=player, amount=5, previous_hp=40, new_hp=45, source=None),
        participants=[player, relic],
    )
    hp_lost_actions = bus.publish(
        HpLostMessage(target=target, amount=3, source=source, card=card),
        participants=[power, target],
    )
    block_actions = bus.publish(
        BlockGainedMessage(target=target, amount=4, source=source, card=card),
        participants=[target, power],
    )
    applied_power = _ReactionPower(owner=target)
    power_actions = bus.publish(
        PowerAppliedMessage(power=applied_power, target=target, owner=player, entities=[]),
        participants=[power, relic],
    )
    death_actions = bus.publish(
        CreatureDiedMessage(creature=target, source=source, card=card, damage_type="attack"),
        participants=[target],
    )

    assert target.damage_taken_triggered is True
    assert source.damage_dealt_triggered is True
    assert power.damage_taken_triggered is True
    assert relic.damage_dealt_triggered is True
    assert relic.heal_triggered is True
    assert power.hp_lost_triggered is True
    assert target.hp_lost_triggered is True
    assert target.block_triggered is True
    assert power.block_triggered is True
    assert power.power_added_triggered is True
    assert relic.power_added_triggered is True
    assert card.damage_dealt_triggered is True
    assert card.fatal_triggered is True
    assert target.death_triggered is True
    assert damage_actions == []
    assert heal_actions == []
    assert hp_lost_actions == []
    assert block_actions == []
    assert power_actions == []
    assert death_actions == []


def test_play_and_attack_messages_use_class_level_subscription_metadata():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=20)
    play_power = _PlayAttackPower(owner=player)
    relic = _PlayAttackRelic()
    hand_card = _PlayReactiveCard()
    player.powers = [play_power]
    player.relics = [relic]

    bus = MessageBus()
    play_actions = bus.publish(
        CardPlayedMessage(card=hand_card, owner=player, targets=[enemy]),
        participants=[play_power, relic, hand_card],
    )
    attack_actions = bus.publish(
        AttackPerformedMessage(target=enemy, source=player, card=hand_card, damage_type="attack"),
        participants=[play_power],
    )

    assert play_power.card_play_triggered is True
    assert relic.card_play_triggered is True
    assert hand_card.card_play_triggered is True
    assert play_power.attack_triggered is True
    assert [type(action).__name__ for action in play_actions] == [
        "GainBlockAction",
        "GainBlockAction",
        "GainBlockAction",
    ]
    assert [type(action).__name__ for action in attack_actions] == ["GainBlockAction"]


def test_damage_resolved_dispatches_to_lagavulin_override():
    lagavulin = Lagavulin(start_awake=False)
    source = _ReactionCreature()
    bus = MessageBus()

    bus.publish(
        DamageResolvedMessage(amount=7, target=lagavulin, source=source, card=None, damage_type="attack"),
        participants=[lagavulin],
    )

    assert lagavulin.is_sleeping is False
    assert lagavulin.is_stunned is True
    assert lagavulin.turns_without_damage == 0


def test_damage_resolved_dispatches_to_the_champ_override_signature():
    class ChampProbe(TheChamp):
        def __init__(self):
            super().__init__()
            self.observed_damage = None

        def on_damage_taken(self, damage: int):
            self.observed_damage = damage
            return TheChamp.on_damage_taken(self, damage)

    champ = ChampProbe()
    champ.hp = champ.max_hp // 2
    bus = MessageBus()

    bus.publish(
        DamageResolvedMessage(amount=9, target=champ, source=None, card=None, damage_type="attack"),
        participants=[champ],
    )

    assert champ.observed_damage == 9
    assert champ.hp == champ.max_hp // 2

# -*- coding: utf-8 -*-
"""Lagavulin - Act 1 Elite enemy"""
from engine.random_streams import get_rng

from enemies.base import Enemy
from utils.types import EnemyType
from utils.registry import register
from enemies.act1.lagavulin_intentions import (
    SleepIntention, StunnedIntention, 
    AttackIntention, SiphonSoulIntention
)


@register("enemy")
class Lagavulin(Enemy):
    enemy_type = EnemyType.ELITE
    
    def __init__(self, ascension: int = 0, start_awake: bool = False):
        from engine.game_state import game_state

        ascension = max(ascension, getattr(game_state, "ascension", 0))
        if ascension >= 8:
            hp = get_rng("monster_hp").randint(112, 115)
        else:
            hp = 110
        
        super().__init__(hp_range=(hp, hp))
        self.ascension = ascension
        self.start_awake = start_awake
        self._stun_pending = False
        self.is_sleeping = not start_awake  # Can start awake for Dead Adventurer event
        self.turns_without_damage = 0
        if not start_awake:
            from powers.definitions.metallicize import MetallicizePower
            self.add_power(MetallicizePower(8, owner=self))

        high_asc = ascension >= 3
        damage = 20 if high_asc else 18
        siphon_amount = 2 if ascension >= 18 else 1

        # Register intentions with keys
        self.add_intention(SleepIntention(self))
        self.add_intention(StunnedIntention(self))
        self.add_intention(AttackIntention(self, damage))
        self.add_intention(SiphonSoulIntention(self, siphon_amount))

    def on_combat_start(self, floor: int = 1) -> None:
        """Sleeping encounters start with 8 Block; event encounters start awake."""
        super().on_combat_start(floor)
        if not self.start_awake:
            self.gain_block(8)

    def determine_next_intention(self, floor: int = 1):
        """Intent queries never advance sleep or the awake attack cycle."""
        if self.is_sleeping:
            return self.intentions["sleep"]
        if self._stun_pending:
            return self.intentions["stunned"]
        completed = sum(name in ("attack", "siphon_soul") for name in self.history_intentions)
        offset = 2 if self.start_awake else 0
        pattern = ("attack", "attack", "siphon_soul")
        return self.intentions[pattern[(completed + offset) % len(pattern)]]

    def _wake_up(self) -> None:
        """Remove the 8 Metallicize supplied by sleeping, preserving other stacks."""
        self.is_sleeping = False
        metallicize = self.get_power("Metallicize")
        if metallicize is not None:
            metallicize.amount -= 8
            if metallicize.amount <= 0:
                self.remove_power(metallicize)

    def finish_sleep_turn(self) -> None:
        """Count actual sleep actions; wake after the third without attacking."""
        if not self.is_sleeping:
            return
        self.turns_without_damage += 1
        if self.turns_without_damage >= 3:
            self._wake_up()
            self.current_intention = self.determine_next_intention()

    def finish_stunned_turn(self) -> None:
        self._stun_pending = False
        self.current_intention = self.determine_next_intention()

    def on_any_hp_lost(self, amount: int, source=None, card=None):
        """Actual HP loss wakes once, replacing this turn's sleep with a stun."""
        if self.is_sleeping and amount > 0:
            self._wake_up()
            self.turns_without_damage = 0
            self._stun_pending = True
            self.current_intention = self.intentions["stunned"]
        return []

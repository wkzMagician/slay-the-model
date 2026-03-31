"""Defect rare power card - Electrodynamics."""

from typing import List

from actions.combat import ApplyPowerAction
from actions.orb import AddOrbAction
from cards.base import Card
from entities.creature import Creature
from orbs.lightning import LightningOrb
from powers.definitions.electro import ElectroPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Electrodynamics(Card):
    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 2
    base_magic = {"lightning": 2}
    upgrade_magic = {"lightning": 3}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        actions = [ApplyPowerAction(ElectroPower(owner=game_state.player), game_state.player)]
        actions.extend(AddOrbAction(LightningOrb()) for _ in range(self.get_magic_value("lightning")))
        add_actions(actions)

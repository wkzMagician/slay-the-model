from __future__ import annotations

from actions.card import AddCardAction, DrawCardsAction
from actions.combat import GainBlockAction, GainEnergyAction
from actions.combat_damage import DealDamageAction, LoseHPAction
from actions.combat_status import ApplyPowerAction, RemovePowerAction
from engine.messages import CardAddedToPileMessage, ScryMessage, StanceChangedMessage
from engine.runtime_api import add_action, add_actions
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from powers.definitions.dexterity import DexterityPower
from powers.definitions.weak import WeakPower
from utils.damage_phase import DamagePhase
from utils.registry import register
from utils.types import CardType, StatusType



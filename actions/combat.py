from typing import TYPE_CHECKING, List

from actions.base import Action
from actions.combat_cards import AttackAction, PlayCardAction, PlayCardBHAction
from actions.combat_damage import DealDamageAction, GainBlockAction, HealAction, LoseHPAction
from actions.combat_status import ApplyPowerAction, RemovePowerAction, UsePotionAction, UsePotionBHAction
from entities.creature import Creature
from localization import t
from engine.runtime_events import emit_text as print
from utils.registry import register
from utils.result_types import BaseResult, NoneResult
from utils.types import CombatType

if TYPE_CHECKING:
    from enemies.base import Enemy


@register("action")
class ModifyMaxHpAction(Action):
    """Modify player's max HP."""

    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> BaseResult:
        from engine.game_state import game_state

        if game_state.player:
            game_state.player.max_hp += self.amount
            print(t("ui.max_hp_changed", default=f"Max HP changed by {self.amount}!", amount=self.amount))
        return NoneResult()


@register("action")
class RemoveEnemyAction(Action):
    """Remove an enemy from combat."""

    def __init__(self, enemy: "Enemy"):
        self.enemy = enemy

    def execute(self) -> BaseResult:
        from engine.game_state import game_state

        if game_state.current_combat:
            game_state.current_combat.remove_enemy(self.enemy)
        return NoneResult()


@register("action")
class AddEnemyAction(Action):
    """Add an enemy to combat."""

    def __init__(self, enemy: "Enemy"):
        self.enemy = enemy

    def execute(self) -> BaseResult:
        from enemies.base import Enemy
        from engine.game_state import game_state

        if game_state.current_combat:
            enemy = self.enemy() if isinstance(self.enemy, type) else self.enemy
            if isinstance(enemy, Enemy):
                game_state.current_combat.add_enemy(enemy)
        return NoneResult()


@register("action")
class GainEnergyAction(Action):
    """Gain energy for the player."""

    def __init__(self, energy):
        self.energy = energy

    def execute(self) -> BaseResult:
        from engine.game_state import game_state

        if game_state.player:
            energy_amount = self.energy() if callable(self.energy) else self.energy
            game_state.player.gain_energy(energy_amount)
            if energy_amount != 0:
                print(t("combat.gain_energy").format(amount=energy_amount))
        return NoneResult()


@register("action")
class EndTurnAction(Action):
    """End the player's turn."""

    def execute(self) -> BaseResult:
        from engine.game_state import game_state

        game_state.current_combat.combat_state.current_phase = "player_end"
        print(t("combat.end_turn"))
        return NoneResult()


@register("action")
class TriggerRelicAction(Action):
    """Trigger a relic's passive or active effect."""

    def __init__(self, relic_name: str):
        self.relic_name = relic_name

    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        from utils.registry import get_registered

        if not game_state.player:
            return NoneResult()

        relic = get_registered("relic", self.relic_name)
        if not relic:
            return NoneResult()

        if hasattr(relic, "on_trigger"):
            relic.on_trigger()
        elif hasattr(relic, "passive"):
            relic.passive()
        return NoneResult()


@register("action")
class StartFightAction(Action):
    """Start a fight with the specified enemies."""

    def __init__(self, enemies: List["Enemy"], combat_type: CombatType = CombatType.NORMAL, victory_actions: List[Action] = None):
        self.enemies = enemies
        self.combat_type = combat_type
        self.victory_actions = victory_actions or []

    def execute(self) -> BaseResult:
        from engine.combat import Combat
        from engine.game_state import game_state

        if not self.enemies:
            return NoneResult()

        combat = Combat(enemies=self.enemies, combat_type=self.combat_type)
        result = combat.start()

        if result.state == "COMBAT_WIN":
            for action in self.victory_actions:
                game_state.action_queue.add_action(action)
            game_state.drive_actions()
            return NoneResult()
        if result.state in {"GAME_LOSE", "COMBAT_ESCAPE"}:
            return result if result.state == "GAME_LOSE" else NoneResult()
        return result


@register("action")
class LoseMaxHPAction(Action):
    """Lose max HP permanently."""

    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> BaseResult:
        from engine.game_state import game_state

        player = game_state.player
        player.max_hp -= self.amount
        player.hp = min(player.hp, player.max_hp)

        print(f"Lost {self.amount} max HP. New max HP: {player.max_hp}")
        return NoneResult()





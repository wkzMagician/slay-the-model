from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from collections.abc import Callable
from typing import TYPE_CHECKING, List

from actions.base import Action
from actions.combat_cards import AttackAction, PlayCardAction, PlayCardBHAction
from actions.combat_damage import DealDamageAction, GainBlockAction, HealAction, LoseHPAction
from actions.combat_status import ApplyPowerAction, RemovePowerAction, UsePotionAction, UsePotionBHAction
from entities.creature import Creature
from localization import t
from engine.runtime_events import emit_text as print
from utils.registry import register
from utils.result_types import GameTerminalState
from utils.types import CombatType

if TYPE_CHECKING:
    from enemies.base import Enemy


@register("action")
class ModifyMaxHpAction(Action):
    """Modify player's max HP."""

    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player:
            game_state.player.max_hp += self.amount
            print(t("ui.max_hp_changed", default=f"Max HP changed by {self.amount}!", amount=self.amount))


@register("action")
class RemoveEnemyAction(Action):
    """Remove an enemy from combat."""

    def __init__(self, enemy: "Enemy"):
        self.enemy = enemy

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.current_combat:
            game_state.current_combat.remove_enemy(self.enemy)


@register("action")
class AddEnemyAction(Action):
    """Add an enemy to combat."""

    def __init__(self, enemy: "Enemy"):
        self.enemy = enemy

    def execute(self) -> None:
        from enemies.base import Enemy
        from engine.game_state import game_state

        if game_state.current_combat:
            enemy = self.enemy() if isinstance(self.enemy, type) else self.enemy
            if isinstance(enemy, Enemy):
                game_state.current_combat.add_enemy(enemy)
                player = getattr(game_state, "player", None)
                if player is not None:
                    for relic in list(getattr(player, "relics", [])):
                        hook = getattr(relic, "on_spawn_monster", None)
                        if callable(hook):
                            hook(enemy, player)


@register("action")
class GainEnergyAction(Action):
    """Gain energy for the player."""

    def __init__(self, energy: int | Callable[[], int]):
        self.energy = energy

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.player:
            energy_amount = self.energy() if callable(self.energy) else self.energy
            energy_amount = int(energy_amount)
            game_state.player.gain_energy(energy_amount)
            if energy_amount != 0:
                print(t("combat.gain_energy").format(amount=energy_amount))


@register("action")
class EndTurnAction(Action):
    """End the player's turn."""

    def execute(self) -> None:
        from engine.game_state import game_state

        if game_state.current_combat is None:
            return
        game_state.current_combat.combat_state.current_phase = "player_end"
        print(t("combat.end_turn"))


@register("action")
class TriggerRelicAction(Action):
    """Trigger a relic's passive or active effect."""

    def __init__(self, relic_name: str):
        self.relic_name = relic_name

    def execute(self) -> None:
        from engine.game_state import game_state
        from utils.registry import get_registered

        if not game_state.player:
            return

        relic = get_registered("relic", self.relic_name)
        if not relic:
            return

        if hasattr(relic, "on_trigger"):
            relic.on_trigger()
        elif hasattr(relic, "passive"):
            relic.passive()


@register("action")
class StartFightAction(Action):
    """Start a fight with the specified enemies."""

    def __init__(
        self,
        enemies: List["Enemy"],
        combat_type: CombatType = CombatType.NORMAL,
        victory_actions: List[Action] | None = None,
    ):
        self.enemies = enemies
        self.combat_type = combat_type
        self.victory_actions = victory_actions or []

    def execute(self) -> None:
        from engine.combat import Combat
        from engine.game_state import game_state

        if not self.enemies:
            return

        combat = Combat(enemies=self.enemies, combat_type=self.combat_type)
        result = combat.start()

        if result == GameTerminalState.COMBAT_WIN:
            for action in self.victory_actions:
                add_action(action)
            game_state.drive_actions()
            return
        if result in {GameTerminalState.GAME_LOSE, GameTerminalState.COMBAT_ESCAPE}:
            if result == GameTerminalState.GAME_LOSE:
                set_terminal_state(result)
            return


@register("action")
class LoseMaxHPAction(Action):
    """Lose max HP permanently."""

    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state

        player = game_state.player
        player.max_hp -= self.amount
        player.hp = min(player.hp, player.max_hp)

        print(f"Lost {self.amount} max HP. New max HP: {player.max_hp}")


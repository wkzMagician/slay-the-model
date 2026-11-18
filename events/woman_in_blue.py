"""
Event 5 - The Woman in Blue
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from events.base_event import Event
from actions.base import LambdaAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import LoseGoldAction, AddRandomPotionAction
from actions.combat import LoseHPAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(
    category="special",
    event_id="woman_in_blue",
    acts='shared',
    weight=100
)
class WomanInBlueEvent(Event):
    """
    The Woman in Blue - Buy potions
    
    [Buy 1 Potion] Lose 20 Gold. Obtain a random potion.
    [Buy 2 Potions] Lose 30 Gold. Obtain 2 random potions.
    [Buy 3 Potions] Lose 40 Gold. Obtain 3 random potions.
    [Leave] A15+: lose 5% of Max HP, rounded up. Otherwise free.
    """
    
    @classmethod
    def can_appear(cls) -> bool:
        from engine.game_state import game_state
        return game_state.player is not None and game_state.player.gold >= 50

    def trigger(self) -> None:
        """Trigger woman in blue encounter"""
        from engine.game_state import game_state
        
        # Collect all actions
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key="events.woman_in_blue.description"
        ))
        
        options = []
        for count, cost in ((1, 20), (2, 30), (3, 40)):
            options.append(Option(
                name=LocalStr("events.woman_in_blue.buy", count=count),
                detail=LocalStr("events.woman_in_blue.buy_detail", count=count, cost=cost),
                actions=[LoseGoldAction(amount=cost),
                         *[AddRandomPotionAction(character=game_state.player.character, uniform=True) for _ in range(count)],
                         LambdaAction(self.end_event)],
            ))

        leave_damage = (game_state.player.max_hp + 19) // 20 if game_state.ascension >= 15 else 0
        options.append(Option(
            name=LocalStr("events.woman_in_blue.option4"),
            detail=LocalStr("events.lose_hp", hp=leave_damage) if leave_damage else LocalStr("events.no_effect"),
            actions=[*([LoseHPAction(amount=leave_damage)] if leave_damage else []),
                     LambdaAction(self.end_event)],
        ))

        # Display options and wait for selection
        actions.append(InputRequestAction(
            title=LocalStr("events.woman_in_blue.title"),
            options=options
        ))
        
        add_actions(actions)

"""
Event 2 - The Cleric

[Heal] Lose 35 Gold. Heal 25% of your Max HP.
[Purify] Lose 50 (75 on A15+) Gold. Remove a card from your deck.
[Leave] Nothing happens.
"""
from utils.result_types import BaseResult
from events.base_event import Event
from actions.card import ChooseRemoveCardAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import LoseGoldAction
from actions.combat import HealAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option


@register_event(
    event_id="the_cleric",
    acts=[1],
    weight=100
)
class TheClericEvent(Event):
    """The Cleric - Heal or remove card for gold"""
    
    def trigger(self) -> 'BaseResult':
        """Trigger clerics encounter event"""
        from utils.result_types import MultipleActionsResult
        from engine.game_state import game_state
        
        # Collect all actions
        actions = []

        # Display event description
        actions.append(DisplayTextAction(
            text_key="events.the_cleric.description"
        ))

        # Determine purify cost based on ascension
        purify_cost = 75 if game_state.ascension >= 15 else 50

        # Build options
        options = []

        # Option 1: Heal - Lose 35 Gold, Heal 25% Max HP
        if game_state.player.gold >= 35:
            heal_amount = game_state.player.max_hp // 4  # 25% of max HP
            options.append(Option(
                name=LocalStr("events.the_cleric.option1"),
                actions=[
                    LoseGoldAction(amount=35),
                    HealAction(amount=heal_amount),
                ]
            ))

        # Option 2: Purify - Lose 50/75 Gold, Remove a card
        if game_state.player.gold >= purify_cost:
            options.append(Option(
                name=LocalStr("events.the_cleric.option2"),
                actions=[
                    LoseGoldAction(amount=purify_cost),
                    ChooseRemoveCardAction(pile="deck", amount=1),
                ]
            ))

        # Option 3: Leave - Nothing happens
        options.append(Option(
            name=LocalStr("events.the_cleric.option3"),
            actions=[]  # Empty actions = nothing happens
        ))

        # Display options and wait for selection
        actions.append(InputRequestAction(
            title=LocalStr("events.the_cleric.title"),
            options=options
        ))

        return MultipleActionsResult(actions)

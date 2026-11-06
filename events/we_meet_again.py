"""Event: We Meet Again! - Shrine Event (All Acts)

Trade a potion, gold, or card for a random relic.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import ChooseRemoveCardAction
from actions.reward import AddRandomRelicAction, LoseGoldAction, LosePotionAction
from utils.types import RarityType
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(category='special', event_id='we_meet_again', acts='shared', weight=100)
class WeMeetAgain(Event):
    """We Meet Again! - trade items for relic."""

    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.we_meet_again.description'
        ))
        
        # Build one demand the player can pay, plus the attack that gives nothing.
        options = []
        demands = []
        if list(game_state.player.potions):
            demands.append("potion")
        if game_state.player.gold >= 50:
            demands.append("gold")
        if any(_offerable_card(card) for card in game_state.player.deck):
            demands.append("card")

        demand = get_rng("misc").choice(demands) if demands else None
        if demand == "potion":
            potion = get_rng("misc").choice(list(game_state.player.potions))
            potion.event_locked = True
            options.append(Option(
                name=(
                    LocalStr('events.we_meet_again.give_potion')
                    + "  "
                    + potion.local("name")
                    + "  "
                    + LocalStr('events.we_meet_again.give_potion_effect')
                ),
                actions=[
                    LosePotionAction(potion=potion),
                    AddRandomRelicAction(),
                ],
            ))
        elif demand == "gold":
            gold_amount = get_rng("misc").randint(50, min(game_state.player.gold, 150))
            options.append(Option(
                name=(
                    LocalStr('events.we_meet_again.give_gold')
                    + "  "
                    + LocalStr('events.we_meet_again.give_gold_effect', amount=gold_amount)
                ),
                actions=[
                    LoseGoldAction(amount=gold_amount),
                    AddRandomRelicAction()
                ]
            ))
        elif demand == "card":
            options.append(Option(
                name=(
                    LocalStr('events.we_meet_again.give_card')
                    + "  "
                    + LocalStr('events.we_meet_again.give_card_effect')
                ),
                actions=[
                    ChooseRemoveCardAction(
                        pile='deck',
                        exclude_rarities=[RarityType.STARTER, RarityType.CURSE],
                        exclude_bottled=True,
                    ),
                    AddRandomRelicAction()
                ]
            ))
        
        # Attack: he runs away and gives nothing.
        options.append(Option(
            name=(
                LocalStr('events.we_meet_again.attack')
                + "  "
                + LocalStr('events.we_meet_again.attack_effect')
            ),
            actions=[]  # Nothing happens
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.we_meet_again.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)


def _offerable_card(card) -> bool:
    return (
        card.rarity not in (RarityType.STARTER, RarityType.CURSE)
        and not getattr(card, "bottled", False)
    )

"""Event: Bonfire Spirits - Shrine Event (All Acts)

Sacrifice a card to the spirits for rewards based on card rarity.
- Basic: Nothing
- Common: Heal 5 HP
- Uncommon: Full heal
- Rare: +10 Max HP + Full heal
- Curse: Receive Spirit Poop relic
"""

from utils.result_types import BaseResult, MultipleActionsResult
from localization import t
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.card import RemoveCardAction
from actions.combat import HealAction, ModifyMaxHpAction
from actions.reward import AddRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from utils.types import RarityType


@register_event(event_id='bonfire_spirits', acts='shared', weight=100)
class BonfireSpirits(Event):
    """Bonfire Spirits - sacrifice card for reward by rarity."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.bonfire_spirits.description'
        ))
        
        # Build options based on cards in deck
        card_options = []
        player = game_state.player
        
        if player and player.card_manager:
            deck = player.card_manager.get_pile('deck')
            for i, card in enumerate(deck):
                # Determine reward based on card rarity
                reward_actions = [RemoveCardAction(card=card, src_pile='deck')]
                
                if card.rarity == RarityType.STARTER:
                    # Basic: Nothing happens
                    pass
                elif card.rarity == RarityType.COMMON:
                    # Common: Heal 5 HP
                    reward_actions.append(HealAction(amount=5))
                elif card.rarity == RarityType.UNCOMMON:
                    # Uncommon: Full heal
                    max_hp = player.max_hp
                    reward_actions.append(HealAction(amount=max_hp))
                elif card.rarity in (RarityType.RARE, RarityType.SPECIAL):
                    # Rare/Legendary: +10 Max HP + Full heal
                    reward_actions.append(ModifyMaxHpAction(amount=10))
                    # Full heal after max HP increase
                    reward_actions.append(HealAction(amount=player.max_hp + 10))
                elif card.rarity == RarityType.CURSE:
                    # Curse: Spirit Poop relic
                    from relics.global_relics.event import SpiritPoop
                    reward_actions.append(AddRelicAction(relic=SpiritPoop()))
                
                card_options.append(Option(
                    name=LocalStr(f'{card.display_name} ({t("ui.rarity." + card.rarity.name.lower(), default=card.rarity.name)})'),
                    actions=reward_actions
                ))
        
        # Add leave option
        options = card_options + [
            Option(
                name=LocalStr('events.bonfire_spirits.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.bonfire_spirits.offer'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)

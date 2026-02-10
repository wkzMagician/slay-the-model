from actions.base import Action
from typing import Optional, Union, List
from cards.base import Card
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered, list_registered
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult, SingleActionResult
            
@register("action")
class RemoveCardAction(Action):
    """Choose a card to remove from src pile
    
    Required:
        card (Card): Card to remove
        src_pile (str): Card location
        
    Optional:
        None
    """
    def __init__(self, card, src_pile: str):
        self.card = card
        self.src_pile = src_pile
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
        return NoneResult()
                
@register("action")
class AddCardAction(Action):
    """Add a specific card to a pile
    
    Required:
        card (Card): Card to add
        dest_pile (str): Destination pile
        
    Optional:
        None
    """
    def __init__(self, card, dest_pile: str):
        self.card = card
        self.dest_pile = dest_pile
        # todo: position argument, default to PilePosType.TOP
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.add_to_pile(self.card, self.dest_pile, pos=PilePosType.TOP)
        return NoneResult()
                
@register("action")
class TransformCardAction(Action):
    """Choose a card to transform from pile
    
    Required:
        card (Card): Card to remove
        pile (str): Card location
        
    Optional:
        reason (str): Transform reason (for UI / logging)
    """
    def __init__(self, card, pile: str, reason: Optional[str] = None):
        self.card = card
        self.pile = pile
        self.reason = reason
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        # 相当于删掉原卡，随机获得一张新卡
        if not game_state.player:
            return NoneResult()

        namespace = self.card.namespace

        # Return actions to be added to caller's action_queue
        return MultipleActionsResult([
            RemoveCardAction(card=self.card, src_pile=self.pile),
            AddCardAction(card=get_random_card(namespaces=[namespace]), dest_pile=self.pile),
        ])

@register("action")
class ExhaustCardAction(Action):
    """Exhaust a card into exhaust pile.

    Required:
        card (Card): Card to exhaust

    Optional:
        source_pile (str): Source pile name
    """
    def __init__(self, card: Card, source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Actually exhaust card
            exhausted = game_state.player.card_manager.exhaust(self.card, src=self.source_pile)
            
            # Trigger card's on_exhaust method
            card_actions = self.card.on_exhaust() if hasattr(self.card, 'on_exhaust') else []
            
            # Trigger on_exhaust powers before exhausting
            power_actions = []
            for power in list(game_state.player.powers):
                if hasattr(power, "on_exhaust"):
                    result = power.on_exhaust()
                    if result:
                        power_actions.extend(result if isinstance(result, list) else [result])
            
            relic_actions = []
            for relic in list(game_state.player.relics):
                if hasattr(relic, "on_exhaust"):
                    result = relic.on_exhaust()
                    if result:
                        relic_actions.extend(result if isinstance(result, list) else [result])

            return MultipleActionsResult(card_actions + power_actions + relic_actions)

        return NoneResult()
    
@register("action")
class DiscardCardAction(Action):
    """Discard a card into discard pile.

    Required:
        card (Card): Card to discard

    Optional:
        source_pile (str): Source pile name
    """
    def __init__(self, card: Card, source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Actually discard card
            discarded = game_state.player.card_manager.discard(self.card, src=self.source_pile)
            
            # Trigger on_discard powers before discarding
            power_actions = []
            if hasattr(game_state.player, 'powers'):
                for power in list(game_state.player.powers):
                    if hasattr(power, "on_discard"):
                        result = power.on_discard(self.card)
                        if result:
                            power_actions.extend(result if isinstance(result, list) else [result])
                        
            # Trigger card's on_discard method
            card_actions = self.card.on_discard() if hasattr(self.card, 'on_discard') else []
            
            return MultipleActionsResult(card_actions + power_actions)
        return NoneResult()
    
@register("action")
class UpgradeCardAction(Action):
    """Upgrade a specific card.
    
    Required:
        card (Card): Card to upgrade
        
    Optional:
        None
    """
    def __init__(self, card):
        self.card = card
    
    def execute(self) -> 'BaseResult':
        if self.card and self.card.can_upgrade():
            self.card.upgrade()
            return NoneResult()
        return NoneResult()
    
@register("action")   
class ChooseRemoveCardAction(Action):
    """Choose a card to remove from hand
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to remove
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        pile = self.pile
        amount = self.amount

        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        RemoveCardAction(card=card, src_pile=pile),
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_remove"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)

@register("action")         
class ChooseTransformCardAction(Action):
    """Choose a card to transform
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to transform
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        TransformCardAction(card=card, pile=pile),
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_transform"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)
      
@register("action")     
class ChooseUpgradeCardAction(Action):
    """Choose a card to upgrade
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to upgrade (-1 to upgrade all)
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            if not card.can_upgrade():
                continue
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        UpgradeCardAction(card)
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_upgrade"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)
    
@register("action")     
class ChooseExhaustCardAction(Action):
    """Choose a card to upgrade
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to upgrade (-1 to upgrade all)
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            if not card.can_upgrade():
                continue
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        ExhaustCardAction(card)
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_exhaust"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)
        
@register("action")      
class ChooseAddRandomCardAction(Action):
    """Choose a random card to add to pile
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        total (int): Total amount of cards to choose from
        namespace (str): Card namespace
        rarity (str): Card rarity
        card_type (CardType): Card type (Attack, Skill, Power)
        temp_cost (int): Temporary cost for the added card (only for current turn)
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', total: int = 3, namespace: Optional[str] = None, rarity: Optional[RarityType] = None,
                 card_type: Optional[CardType] = None, temp_cost: Optional[int] = None):
        self.pile = pile
        self.total = total
        self.namespace = namespace
        self.rarity = rarity
        self.card_type = card_type
        self.temp_cost = temp_cost
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        from actions.display import SelectAction

        options = []
        for _ in range(self.total):
            random_card = get_random_card(
                namespaces=[self.namespace] if self.namespace else None,
                rarities=[self.rarity] if self.rarity else None,
                card_types=[self.card_type] if self.card_type else None
            )
            if not random_card:
                continue
            # * 设置临时能量
            if self.temp_cost is not None:
                random_card.temp_cost = self.temp_cost
            option = random_card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        AddCardAction(card=random_card, dest_pile=self.pile),
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = 1,
            must_select = False, # ? 是否全部都是，可以跳过
        )
        return SingleActionResult(select_action)   
        
@register("action")   
class AddRandomCardAction(Action):
    """Obtain a random card

    Required:
        pile (str): Card location ('deck' or 'hand')
        namespace (str): Card namespace
        card_type (CardType): Card type
        rarity (str): Card rarity

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', card_type: Optional[CardType] = None, rarity: Optional[RarityType] = None, namespace: Optional[str] = None):
        self.pile = pile
        self.card_type = card_type
        self.rarity = rarity
        self.namespace = namespace
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        random_card = get_random_card(
            namespaces=[self.namespace if self.namespace else game_state.player.character],
            card_types=[self.card_type] if self.card_type else None,
            rarities=[self.rarity] if self.rarity else None
        )

        # Return AddCardAction to be added to caller's action_queue
        return SingleActionResult(AddCardAction(card=random_card, dest_pile=self.pile))

@register("action")
class DrawCardsAction(Action):
    """Draw cards from draw pile

    Required:
        count (int): Number of cards to draw

    Optional:
        None
    """
    def __init__(self, count: int):
        self.count = count

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if game_state.player and hasattr(game_state.player, "card_manager"):
            # Draw cards from draw pile to hand
            cards: List[Card] = game_state.player.card_manager.draw_many(self.count)
            
            # Trigger on_card_draw powers for each drawn card
            power_actions = []
            for card in cards:
                if hasattr(game_state.player, 'powers'):
                    for power in list(game_state.player.powers):
                        if hasattr(power, "on_card_draw"):
                            result = power.on_card_draw(card)
                            if result:
                                power_actions.extend(result if isinstance(result, list) else [result])
                
                # Also trigger card's on_draw method
                card_actions = card.on_draw() if hasattr(card, 'on_draw') else []
                power_actions.extend(card_actions)
            
            # If there are any actions from powers/card callbacks, queue them
            if power_actions:
                from utils.result_types import MultipleActionsResult
                return MultipleActionsResult(power_actions)
            
            return NoneResult()

        return NoneResult()
    
@register("action")
class ReplaceCardAction(Action):
    """Discard the card and draw one
    
    Required:
        card (Card): the card to replcae
        
    Optional:
        None
    """
    def __init__(self, card: Card):
        self.card = card
        
    def execute(self) -> 'BaseResult':
        return MultipleActionsResult([
            DiscardCardAction(self.card),
            DrawCardsAction(count=1)
        ])
        
@register("action")
class ChooseReplaceCardAction(Action):
    """
    Choose a card to be replaced.
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to remove
        
    Optional:
        None
    """
    
    def __init__(self, pile: str = 'hand', amount: int = -1, must_select: bool = False):
        self.pile = pile
        self.amount = amount
        self.must_select = must_select
    
    def execute(self) -> 'BaseResult':
        options = []
        from engine.game_state import game_state
        from actions.display import SelectAction
        hand = game_state.player.card_manager.get_pile('hand')
        for card in hand:
            option_name = card.display_name
            options.append(
                Option(
                    name = option_name,
                    actions = [
                        ReplaceCardAction(card),
                    ]
                )
            )
        select_action = SelectAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = self.amount,
            must_select = self.must_select
        )
        return SingleActionResult(select_action)  

@register("action")
class ChooseMoveCardAction(Action):
    """Choose a card to move from one pile to another

    Required:
        src (str): Source pile name
        dst (str): Destination pile name
        amount (int): Amount of cards to move

    Optional:
        None
    """
    def __init__(self, src: str, dst: str, amount: int = 1):
        self.src = src
        self.dst = dst
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        src_pile = self.src
        dst_pile = self.dst
        amount = self.amount

        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(src_pile)

        for card in cards_in_pile:
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        MoveCardAction(card=card, src_pile=src_pile, dst_pile=dst_pile),
                    ]
                )
            )

        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_move"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)

@register("action")
class ChooseCopyCardAction(Action):
    """Choose a card to copy and add to hand

    Required:
        pile (str): Source pile name ('hand' or 'deck')
        copies (int): Number of copies to make

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', copies: int = 1):
        self.pile = pile
        self.copies = copies

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        pile = self.pile
        copies = self.copies

        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            option = card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        CopyCardAction(card=card),
                    ]
                )
            )

        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_copy"),
            options = options,
            max_select = copies,
            must_select = True
        )
        return SingleActionResult(select_action)

@register("action")
class MoveCardAction(Action):
    """Move a specific card from one pile to another

    Required:
        card (Card): Card to move
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name

    Optional:
        None
    """
    def __init__(self, card, src_pile: str, dst_pile: str):
        self.card = card
        self.src_pile = src_pile
        self.dst_pile = dst_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                game_state.player.card_manager.add_to_pile(self.card, self.dst_pile, pos=PilePosType.TOP)
        return NoneResult()

@register("action")
class CopyCardAction(Action):
    """Copy a card and add to hand

    Required:
        card (Card): Card to copy

    Optional:
        None
    """
    def __init__(self, card):
        self.card = card

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                from utils.types import PilePosType
                game_state.player.card_manager.add_to_pile(self.card, "hand", pos=PilePosType.TOP)
        return NoneResult()

@register("action")
class ExhaustRandomCardAction(Action):
    """Exhaust random cards from a pile

    Required:
        pile (str): Source pile name
        amount (int): Number of cards to exhaust

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        import random

        if not game_state.player:
            return NoneResult()

        card_manager = game_state.player.card_manager
        cards_in_pile = list(card_manager.get_pile(self.pile))

        if not cards_in_pile:
            return NoneResult()

        amount_to_exhaust = min(self.amount, len(cards_in_pile))
        cards_to_exhaust = random.sample(cards_in_pile, amount_to_exhaust)

        actions = []
        for card in cards_to_exhaust:
            actions.append(ExhaustCardAction(card=card, source_pile=self.pile))

        if actions:
            return MultipleActionsResult(actions)
        return NoneResult()   

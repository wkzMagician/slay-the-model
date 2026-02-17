from actions.base import Action
from typing import Optional, Union, List, TYPE_CHECKING
from actions.display import SelectAction
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered, list_registered
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card
from utils.result_types import BaseResult, NoneResult, MultipleActionsResult, SingleActionResult

# Type hints only (avoid circular imports)
if TYPE_CHECKING:
    from cards.base import Card
            
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
        source (str): Source of card ("reward", "enemy", etc.)
        position (PilePosType): Position in pile (TOP or BOTTOM), default TOP
    """
    def __init__(self, card, dest_pile: str, source: str = "reward", position: PilePosType = PilePosType.TOP):
        self.card = card
        self.dest_pile = dest_pile
        self.source = source
        self.position = position

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.add_to_pile(self.card, self.dest_pile, pos=self.position)
                # Only show [Reward] for actual rewards, use appropriate prefix for others
                if self.source == "reward":
                    print(f"[Reward] Added {self.card.display_name.resolve()} to {self.dest_pile}")
                elif self.source == "enemy":
                    print(f"[Enemy] Added {self.card.display_name.resolve()} to {self.dest_pile}")
                else:
                    print(f"[{self.source.title()}] Added {self.card.display_name.resolve()} to {self.dest_pile}")
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
    def __init__(self, card: "Card", source_pile: Optional[str] = None):
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
    def __init__(self, card: "Card", source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Find source pile if not specified
            if self.source_pile is None:
                self.source_pile = game_state.player.card_manager.get_card_location(self.card)
            
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
        upgrade (bool)
        namespace (str): Card namespace
        card_type (CardType): Card type
        rarity (str): Card rarity
        permanent_cost (int)
        temp_cost (int)

    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', upgrade: bool = False,
                 card_type: Optional[CardType] = None, rarity: Optional[RarityType] = None, namespace: Optional[str] = None,
                 permanent_cost: Optional[int] = None, temp_cost: Optional[int] = None):
        self.pile = pile
        self.upgrade = upgrade
        self.card_type = card_type
        self.rarity = rarity
        self.namespace = namespace
        self.permanent_cost = permanent_cost
        self.temp_cost = temp_cost
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        random_card = get_random_card(
            namespaces=[self.namespace if self.namespace else game_state.player.character.lower()],
            card_types=[self.card_type] if self.card_type else None,
            rarities=[self.rarity] if self.rarity else None
        )
        
        assert random_card is not None
        
        if self.upgrade:
            random_card.upgrade()
        if self.permanent_cost:
            random_card.cost = self.permanent_cost
        if self.temp_cost:
            random_card.temp_cost = self.temp_cost

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
            # Handle callable count (dynamic card draw amounts)
            count = self.count() if callable(self.count) else self.count
            # Draw cards from draw pile to hand
            cards: List[Card] = game_state.player.card_manager.draw_many(count)
            
            # Note: Draw message is now printed in CombatState._print_combat_state()
            # after "Player Turn" header for better display order
            
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
    def __init__(self, card: "Card"):
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
        filter_card_type (CardType)

    Optional:
        None
    """
    def __init__(self, src: str, dst: str, amount: int = 1, filter_card_type: Optional[CardType] = None):
        self.src = src
        self.dst = dst
        self.amount = amount
        self.filter_card_type = filter_card_type

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
        
        if self.filter_card_type is not None:
            final_pile = []
            for card in cards_in_pile:
                if card.card_type == self.filter_card_type:
                    final_pile.append(card)
            cards_in_pile = final_pile

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

@register("action")
class ShuffleAction(Action):
    """Shuffle all cards from hand and discard piles into draw pile."""

    def execute(self):
        """Execute shuffle: move all cards from hand/discard to draw pile and shuffle."""
        from engine.game_state import game_state
        import random

        if not game_state.player or not hasattr(game_state.player, "card_manager"):
            return NoneResult()

        card_manager = game_state.player.card_manager

        # Collect all cards from hand and discard
        hand_cards = list(card_manager.get_pile("hand"))
        discard_cards = list(card_manager.get_pile("discard_pile"))

        # Add them to draw pile
        for card in hand_cards:
            card_manager.move_to(card=card, dst="draw_pile")
        for card in discard_cards:
            card_manager.move_to(card, "draw_pile")

        # Combine and shuffle
        draw_cards = card_manager.get_pile("draw_pile")
        random.shuffle(draw_cards)
        
        # Trigger on_shuffle relics
        relic_actions = []
        if hasattr(game_state.player, 'relics'):
            for relic in list(game_state.player.relics):
                if hasattr(relic, "on_shuffle"):
                    result = relic.on_shuffle()
                    if result:
                        relic_actions.extend(result if isinstance(result, list) else [result])
        
        # If there are any actions from relic callbacks, queue them
        if relic_actions:
            return MultipleActionsResult(relic_actions)
        
        return NoneResult()

@register("action")
class UpgradeRandomCardAction(Action):
    """Upgrade a random card from player's deck.
    
    Required:
        card_type (CardType): Type of cards to choose from (Attack/Skill/Power)
        count (int): Number of cards to upgrade
    
    Optional:
        namespace (str): Card namespace (default: player's character)
    """
    def __init__(self, card_type: Optional[str] = None, count: int = 1, 
                 namespace: Optional[str] = None):
        self.card_type = card_type
        self.count = count
        self.namespace = namespace
    
    def execute(self) -> 'BaseResult':
        """Execute: choose random cards to upgrade"""
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()
        
        from utils.types import CardType
        
        # Get deck
        deck = game_state.player.card_manager.get_pile('deck')
        
        if not deck:
            return NoneResult()
        
        # Filter cards by type (if specified) and that can be upgraded
        cards_to_choose = []
        for card in deck:
            if not card.can_upgrade():
                continue
            if self.card_type is not None:
                # Match card type
                if self.card_type == "Attack" and card.card_type != CardType.ATTACK:
                    continue
                elif self.card_type == "Skill" and card.card_type != CardType.SKILL:
                    continue
                elif self.card_type == "Power" and card.card_type != CardType.POWER:
                    continue
            
            cards_to_choose.append(card)
        
        # Use specified namespace or default to player's character
        card_namespace = self.namespace if self.namespace else game_state.player.namespace
        
        # Filter cards by namespace if specified
        if self.namespace is not None:
            cards_to_choose = [c for c in cards_to_choose if c.namespace == card_namespace]
        
        if not cards_to_choose:
            print(t("ui.no_upgradeable_cards", default="No upgradeable cards found"))
            return NoneResult()
        
        # If requesting more than available, reduce to available
        actual_count = min(self.count, len(cards_to_choose))
        
        if actual_count == 1:
            # Auto-upgrade if only 1 requested
            return SingleActionResult(UpgradeCardAction(card=cards_to_choose[0]))
        else:
            # Import for use in option actions
            from actions.card import UpgradeCardAction as _UpgradeCardAction
            # Let player choose from multiple cards
            options = []
            for card in cards_to_choose[:actual_count]:
                options.append(Option(
                    name=card.display_name,
                    actions=[UpgradeCardAction(card=card)]
                ))
            
            select_action = SelectAction(
                title=LocalStr("ui.choose_card_to_upgrade"),
                options=options,
                max_select=actual_count,
                must_select=False
            )
            
            return SingleActionResult(select_action)
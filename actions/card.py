from actions.base import Action
from typing import Optional
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered, list_registered
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card
            
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
    
    def execute(self):
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                
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
    
    def execute(self):
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.add_to_pile(self.card, self.dest_pile, pos=PilePosType.TOP)
                
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
    
    def execute(self):
        # 相当于删掉原卡，随机获得一张新卡
        from engine.game_state import game_state
        if not game_state.player:
            return
        namespace = self.card.namespace # ??
        
        # Return actions to be added to caller's action_queue
        return [
            RemoveCardAction(card=self.card, src_pile=self.pile),
            AddCardAction(card=get_random_card(namespaces=[namespace]), dest_pile=self.pile),
        ]

@register("action")
class ExhaustCardAction(Action):
    """Exhaust a card into exhaust pile.

    Required:
        card (Card): Card to exhaust

    Optional:
        source_pile (str): Source pile name
    """
    def __init__(self, card, source_pile: Optional[str] = None):
        self.card = card
        self.source_pile = source_pile

    def execute(self):
        from engine.game_state import game_state
        if self.card and game_state.player and hasattr(game_state.player, "card_manager"):
            # Trigger on_exhaust powers before exhausting
            if hasattr(game_state.player, 'powers'):
                for power in list(game_state.player.powers):
                    if hasattr(power, "on_exhaust"):
                        result = power.on_exhaust(self.card)
                        if result and isinstance(result, list):
                            # Return power actions before exhausting card
                            return result

            # Trigger card's on_exhaust method
            card_actions = self.card.on_exhaust()

            # Actually exhaust the card
            exhausted = game_state.player.card_manager.exhaust(self.card, src=self.source_pile)

            # Add card actions to result
            if card_actions:
                if exhausted is False or exhausted is None:
                    exhausted = []
                elif not isinstance(exhausted, list):
                    exhausted = []

                exhausted.extend(card_actions)
                return exhausted

            return exhausted
        return False
    
class UpgradeCardAction(Action):
    """Upgrade a specific card.
    
    Required:
        card (Card): Card to upgrade
        
    Optional:
        None
    """
    def __init__(self, card):
        self.card = card
    
    def execute(self):
        if self.card and self.card.can_upgrade():
            self.card.upgrade()
            return True
        return False
    
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
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        # * build SelecAction options
        
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction
        
        # todo: 暂时只支持单选
        for _ in range(amount):
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
                options = options
            )
            # Return SelectAction to be added to caller's action_queue
            return select_action
            
        # todo: print remove info message

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
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        # * build SelecAction options
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction
        
        # todo: 暂时只支持单选
        for _ in range(amount):
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
                options = options
            )
            # Return SelectAction to be added to caller's action_queue
            return select_action
            
        # todo: print transform info message
      
@register("action")     
class ChooseUpgradeCardAction(Action):
    """Choose a card to upgrade
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to upgrade
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        # * build SelecAction options
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction
        
        # todo: 暂时只支持单选
        for _ in range(amount):
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
                options = options
            )
            # Return SelectAction to be added to caller's action_queue
            return select_action
            
        # todo: print upgrade info message
        
@register("action")      
class ChooseAddRandomCardAction(Action):
    """Choose a random card to add to pile
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        total (int): Total amount of cards to choose from
        namespace (str): Card namespace
        rarity (str): Card rarity
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', total: int = 3, namespace: Optional[str] = None, rarity: Optional[RarityType] = None):
        self.pile = pile
        self.total = total
        self.namespace = namespace
        self.rarity = rarity
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        
        # 构造 SelectAction options
        from actions.display import SelectAction
        
        options = []
        for _ in range(self.total):
            random_card = get_random_card(
                namespaces=[self.namespace] if self.namespace else None,
                rarities=[self.rarity] if self.rarity else None
            )
            if not random_card:
                continue
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
            options = options
        )
        # Return SelectAction to be added to caller's action_queue
        return select_action
        
        # todo: print add card info message       
        
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
    def __init__(self, pile: str = 'hand', card_type: Optional[CardType] = None, rarity: Optional[RarityType] = None):
        self.pile = pile
        self.card_type = card_type
        self.rarity = rarity
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        
        random_card = get_random_card(
            namespaces=[game_state.player.character],
            card_types=[self.card_type] if self.card_type else None,
            rarities=[self.rarity] if self.rarity else None
        )
        
        # Return AddCardAction to be added to caller's action_queue
        return AddCardAction(card=random_card, dest_pile=self.pile)
        
        # todo: print add card info message

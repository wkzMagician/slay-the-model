from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from actions.base import Action
from typing import List, Optional, TYPE_CHECKING
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card, get_random_card_reward
if TYPE_CHECKING:
    from cards.base import Card

from actions.card_lifecycle import AddCardAction, ExhaustCardAction, RemoveCardAction, ReplaceCardAction
from actions.combat import ModifyMaxHpAction
from actions.card_transform import TransformAndUpgradeCardAction, TransformCardAction, UpgradeCardAction

class ChooseRemoveCardAction(Action):
    """Choose a card to remove from pile
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to remove
        
    Optional:
        exclude_card_types (List[CardType]): Card types to exclude
        exclude_rarities (List[RarityType]): Rarities to exclude
        exclude_bottled (bool): Exclude bottled cards (default False)
    """
    def __init__(self, pile: str = 'hand', amount: int = 1,
                 exclude_card_types: Optional[List] = None,
                 exclude_rarities: Optional[List] = None,
                 exclude_bottled: bool = False):
        self.pile = pile
        self.amount = amount
        self.exclude_card_types = exclude_card_types
        self.exclude_rarities = exclude_rarities
        self.exclude_bottled = exclude_bottled
        
    def execute(self) -> None:
        from engine.game_state import game_state
        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(self.pile)

        for card in cards_in_pile:
            # Filter by card type
            if self.exclude_card_types and card.card_type in self.exclude_card_types:
                continue
            # Filter by rarity
            if self.exclude_rarities and card.rarity in self.exclude_rarities:
                continue
            # Filter bottled cards
            if self.exclude_bottled and hasattr(card, 'bottled') and card.bottled:
                continue
            
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        RemoveCardAction(card=card, src_pile=self.pile),
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_remove"),
            options = options,
            max_select = self.amount,
            must_select = True
        )
        add_action(select_action, to_front=True)

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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        from actions.combat import ModifyMaxHpAction
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        TransformCardAction(card=card, pile=pile),
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_transform"),
            options = options,
            max_select = amount,
            must_select = True
        )
        add_action(select_action, to_front=True)

@register("action")     
class ChooseUpgradeCardAction(Action):
    """Choose a card to upgrade
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to upgrade (-1 to upgrade all)
        exclude_cards (List[Card])
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', amount: int = 1, exclude_cards: List['Card'] = []):
        self.pile = pile
        self.amount = amount
        self.exclude_cards = exclude_cards
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            if not card.can_upgrade():
                continue
            if card in self.exclude_cards:
                continue
            
            # Create an upgraded copy so the preview shows post-upgrade values.
            upgraded_card = card.copy()
            upgraded_card.upgrade()
            
            # Build a compact upgrade preview: name + cost change + description change.
            from localization import ConcatLocalStr
            from utils.dynamic_values import resolve_card_value
            
            # Resolve costs.
            before_cost = resolve_card_value(card, 'cost')
            after_cost = resolve_card_value(upgraded_card, 'cost')
            
            # Resolve descriptions.
            before_desc = card.description.resolve() if hasattr(card, 'description') else ""
            after_desc = upgraded_card.description.resolve() if hasattr(upgraded_card, 'description') else ""
            
            # Format the upgrade preview.
            cost_display = f"{before_cost}"
            if before_cost != after_cost:
                cost_display = f"{before_cost}->{after_cost}"
            
            # If the description does not change, show it only once.
            if before_desc == after_desc:
                option = ConcatLocalStr(
                    card.display_name,
                    f" ({cost_display}) {before_desc}"
                )
            else:
                option = ConcatLocalStr(
                    card.display_name,
                    f" ({cost_display}) {before_desc} -> {after_desc}"
                )
            
            options.append(
                Option(
                    name = option,
                    actions = [
                        UpgradeCardAction(card)
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_upgrade"),
            options = options,
            max_select = amount,
            must_select = True
        )
        add_action(select_action, to_front=True)

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
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            if not card.can_upgrade():
                continue
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        ExhaustCardAction(card)
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_exhaust"),
            options = options,
            max_select = amount,
            must_select = True
        )
        add_action(select_action, to_front=True)

@register("action")      
class ChooseAddRandomCardAction(Action):
    """Choose a random card to add to pile
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        total (int): Total amount of cards to choose from
        namespace (str): Card namespace
        rarity (str): Card rarity
        card_type (CardType): Card type (Attack, Skill, Power)
        cost_until_end_of_turn (int): Cost override for the added card until end of turn
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'hand', total: int = 3, namespace: Optional[str] = None, rarity: Optional[RarityType] = None,
                 card_type: Optional[CardType] = None, cost_until_end_of_turn: Optional[int] = None):
        self.pile = pile
        self.total = total
        self.namespace = namespace
        self.rarity = rarity
        self.card_type = card_type
        self.cost_until_end_of_turn = cost_until_end_of_turn
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        from actions.display import InputRequestAction

        options = []
        selected_card_ids = []  # Track selected cards to avoid duplicates
        for _ in range(self.total):
            random_card = get_random_card(
                namespaces=[self.namespace] if self.namespace else None,
                rarities=[self.rarity] if self.rarity else None,
                card_types=[self.card_type] if self.card_type else None,
                exclude_card_ids=selected_card_ids,  # Exclude already selected cards
                exclude_starter=True  # Exclude STARTER rarity from rewards
            )
            if not random_card:
                continue
            selected_card_ids.append(random_card.idstr)  # Track this card
            # Apply a temporary cost override to the generated card.
            if self.cost_until_end_of_turn is not None:
                random_card.cost_until_end_of_turn = self.cost_until_end_of_turn
            option = random_card.info() # random_card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        AddCardAction(card=random_card, dest_pile=self.pile),
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = 1,
            must_select = False,  # Allow skipping if none of the options are desirable.
        )
        add_action(select_action, to_front=True)

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
    
    def execute(self) -> None:
        options = []
        from engine.game_state import game_state
        from actions.display import InputRequestAction
        hand = game_state.player.card_manager.get_pile('hand')
        for card in hand:
            option_name = card.info() # card.display_name
            options.append(
                Option(
                    name = option_name,
                    actions = [
                        ReplaceCardAction(card),
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = self.amount,
            must_select = self.must_select
        )
        add_action(select_action, to_front=True)

@register("action")
class ChooseMoveCardAction(Action):
    """Choose a card to move from one pile to another

    Required:
        src (str): Source pile name
        dst (str): Destination pile name
        amount (int): Amount of cards to move
        filter_card_type (CardType)

    Optional:
        position (PilePosType): Position in destination pile (TOP or BOTTOM), default TOP
    """
    def __init__(self, src: str, dst: str, amount: int = 1, filter_card_type: Optional[CardType] = None, position: PilePosType = PilePosType.TOP):
        self.src = src
        self.dst = dst
        self.amount = amount
        self.filter_card_type = filter_card_type
        self.position = position

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        src_pile = self.src
        dst_pile = self.dst
        amount = self.amount

        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(src_pile)
        
        if self.filter_card_type is not None:
            final_pile = []
            for card in cards_in_pile:
                if card.card_type == self.filter_card_type:
                    final_pile.append(card)
            cards_in_pile = final_pile

        for card in cards_in_pile:
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        MoveCardAction(card=card, src_pile=src_pile, dst_pile=dst_pile, position=self.position),
                    ]
                )
            )

        if not options:
            return
        if len(options) == 1 and amount == 1:
            add_actions(options[0].actions, to_front=True)
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_move"),
            options = options,
            max_select = amount,
            must_select = True
        )
        add_action(select_action, to_front=True)


@register("action")
class ChooseDiscardCardAction(Action):
    """Choose cards from hand to discard using DiscardCardAction semantics."""

    def __init__(self, pile: str = 'hand', amount: int = 1, must_select: bool = True):
        self.pile = pile
        self.amount = amount
        self.must_select = must_select

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        from actions.card_lifecycle import DiscardCardAction
        from actions.display import InputRequestAction

        options = []
        for card in game_state.player.card_manager.get_pile(self.pile):
            options.append(
                Option(
                    name=card.info(),
                    actions=[DiscardCardAction(card=card, source_pile=self.pile)],
                )
            )

        if not options:
            return
        if len(options) == 1 and self.amount == 1:
            add_actions(options[0].actions, to_front=True)
            return
        add_action(
            InputRequestAction(
                title=LocalStr("ui.choose_cards_to_move"),
                options=options,
                max_select=self.amount,
                must_select=self.must_select,
            ),
            to_front=True,
        )

@register("action")
class ChooseCopyCardAction(Action):
    """Choose a card to copy and add to hand

    Required:
        pile (str): Source pile name ('hand' or 'deck')
        copies (int): Number of copies to make

    Optional:
        card_types (List[CardType]): List of allowed card types. If None, all types are allowed.
    """
    def __init__(self, pile: str = 'hand', copies: int = 1, card_types: Optional[List['CardType']] = None):
        self.pile = pile
        self.copies = copies
        self.card_types = card_types

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        pile = self.pile
        copies = self.copies
        card_types = self.card_types

        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            # Filter by card types if specified
            if card_types is not None:
                if card.card_type not in card_types:
                    continue
                
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        CopyCardAction(card=card),
                    ]
                )
            )

        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_copy"),
            options = options,
            max_select = copies,
            must_select = True
        )
        add_action(select_action, to_front=True)

@register("action")
class MoveCardAction(Action):
    """Move a specific card from one pile to another

    Required:
        card (Card): Card to move
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name

    Optional:
        position (PilePosType): Position in destination pile (TOP or BOTTOM), default TOP
    """
    def __init__(self, card, src_pile: str, dst_pile: str, position: PilePosType = PilePosType.TOP):
        self.card = card
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.position = position

    def execute(self) -> None:
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                game_state.player.card_manager.add_to_pile(self.card, self.dst_pile, pos=self.position)

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

    def execute(self) -> None:
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                from utils.types import PilePosType
                game_state.player.card_manager.add_to_pile(self.card, "hand", pos=PilePosType.TOP)

@register("action")
class SetCostUntilEndOfTurnAction(Action):
    """Set cost override for this turn only.

    Required:
        card (Card): Card to modify
        cost_until_end_of_turn (int): Temporary cost value (None to reset)

    Optional:
        None
    """
    def __init__(self, card: "Card", cost_until_end_of_turn: Optional[int]):
        self.card = card
        self.cost_until_end_of_turn = cost_until_end_of_turn

    def execute(self) -> None:
        if self.card:
            self.card.cost_until_end_of_turn = self.cost_until_end_of_turn


@register("action")
class SetCostUntilPlayedAction(Action):
    """Set a persistent cost override that lasts until the card is played."""

    def __init__(self, card: "Card", cost: Optional[int]):
        self.card = card
        self.cost = cost

    def execute(self) -> None:
        if self.card:
            self.card.cost_until_played = self.cost

@register("action")
class MoveAndSetCostAction(Action):
    """Move a card and set its cost until played.
    
    Used by Forethought card: move card to bottom of draw pile, 
    and set its cost to 0 until played.

    Required:
        card (Card): Card to move
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name
        cost_until_played (int): Cost override to keep until the card is played

    Optional:
        position (PilePosType): Position in destination pile (default BOTTOM)
    """
    def __init__(self, card: "Card", src_pile: str, dst_pile: str, 
                 cost_until_played: int = 0, position: PilePosType = PilePosType.BOTTOM):
        self.card = card
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.cost_until_played = cost_until_played
        self.position = position

    def execute(self) -> None:
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                # Move the card
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                game_state.player.card_manager.add_to_pile(self.card, self.dst_pile, pos=self.position)
                self.card.cost_until_played = self.cost_until_played

@register("action")
class ChooseMoveAndSetCostAction(Action):
    """Choose cards to move and set their temporary cost.
    
    Used by Forethought card: choose cards from hand, move to bottom 
    of draw pile, and set their cost to 0 until played.

    Required:
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name
        amount (int): Number of cards to choose (-1 for any number)
        cost_until_played (int): Cost override to set until played (default 0)

    Optional:
        position (PilePosType): Position in destination pile (default BOTTOM)
        must_select (bool): Whether selection is required (default True)
    """
    def __init__(self, src_pile: str, dst_pile: str, amount: int = 1, 
                 cost_until_played: int = 0, position: PilePosType = PilePosType.BOTTOM,
                 must_select: bool = True):
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.amount = amount
        self.cost_until_played = cost_until_played
        self.position = position
        self.must_select = must_select

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(self.src_pile)

        for card in cards_in_pile:
            option = card.info()
            options.append(
                Option(
                    name=option,
                    actions=[
                        MoveAndSetCostAction(
                            card=card, 
                            src_pile=self.src_pile, 
                            dst_pile=self.dst_pile,
                            cost_until_played=self.cost_until_played,
                            position=self.position
                        ),
                    ]
                )
            )

        if not options:
            return
        
        # amount = -1 means any number of cards
        max_select = self.amount if self.amount > 0 else len(cards_in_pile)
        
        select_action = InputRequestAction(
            title=LocalStr("ui.choose_cards_to_set_cost"),
            options=options,
            max_select=max_select,
            must_select=self.must_select
        )
        add_action(select_action, to_front=True)

@register("action")
class ChooseTransformAndUpgradeAction(Action):
    """Choose cards to transform and upgrade.
    
    Used by Astrolabe relic: Choose 3 cards, transform each into a random 
    card of the same color, then upgrade them.
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to transform (default 3 for Astrolabe)
        
    Optional:
        None
    """
    def __init__(self, pile: str = 'deck', amount: int = 3):
        self.pile = pile
        self.amount = amount
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import InputRequestAction

        options = []
        cards_in_pile = card_manager.get_pile(pile)

        for card in cards_in_pile:
            option = card.info() # card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        TransformAndUpgradeCardAction(card=card, pile=pile),
                    ]
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_cards_to_transform_and_upgrade"),
            options = options,
            max_select = amount,
            must_select = True
        )
        add_action(select_action, to_front=True)

@register("action")      
class ChooseObtainCardAction(Action):
    """Choose a 1/N card to add to deck
    
    Required:
        total (int): Total amount of cards to choose from
        namespace (str): Card namespace
        encounter_type (str): Type of encounter for rarity weights ("normal", "elite", "shop").
        use_rolling_offset (bool): If True, adjust rare chance based on common cards gained.
        exclude_set (Optional[List[str]]): List of card idstrs to exclude (prevents duplicates)
        pile (str): Destination pile for selected card
        allow_upgraded (bool): Whether rewards can roll upgraded cards.
        
    Optional:
        None
    """
    def __init__(self, total: int = 3, namespace: Optional[str] = None, 
                 encounter_type: str = "normal", use_rolling_offset: bool = False,
                 exclude_set: Optional[List[str]] = None, pile: str = "deck",
                 allow_upgraded: bool = False):
        self.total = total
        self.namespace = namespace
        self.encounter_type = encounter_type
        self.use_rolling_offset = use_rolling_offset
        self.exclude_set = exclude_set or []
        self.pile = pile
        self.allow_upgraded = allow_upgraded
    
    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return

        from actions.display import InputRequestAction

        reward_namespace = self.namespace
        has_prismatic_shard = any(
            getattr(relic, "idstr", None) == "PrismaticShard"
            for relic in game_state.player.relics
        )
        if has_prismatic_shard:
            reward_namespace = None

        options = []
        selected_card_ids = list(self.exclude_set)  # Track selected cards to avoid duplicates
        for _ in range(self.total):
            random_card = get_random_card_reward(
                namespaces=[reward_namespace] if reward_namespace else None,
                encounter_type=self.encounter_type,
                use_rolling_offset=self.use_rolling_offset,
                exclude_set=selected_card_ids,
                allow_upgraded=self.allow_upgraded,
            )
            if not random_card:
                continue
            if self.pile in ("deck"):
                for relic in list(game_state.player.relics):
                    hook = getattr(relic, "should_upgrade_added_card", None)
                    if hook and hook(random_card, self.pile) and random_card.can_upgrade():
                        random_card.upgrade()
            selected_card_ids.append(random_card.idstr)  # Track to avoid duplicates in next iteration
            option = random_card.info() # random_card.display_name
            options.append(
                Option(
                    name = option,
                    actions = [
                        AddCardAction(card=random_card, dest_pile=self.pile),
                    ]
                )
            )
        can_singing_bowl = any(
            getattr(relic, "idstr", None) == "SingingBowl"
            and callable(getattr(relic, "can_choose_max_hp_instead_of_card", None))
            and getattr(relic, "can_choose_max_hp_instead_of_card")()
            for relic in game_state.player.relics
        )
        if can_singing_bowl:
            options.append(
                Option(
                    name=LocalStr("ui.gain_max_hp_instead", default="Gain +2 Max HP"),
                    actions=[ModifyMaxHpAction(amount=2)],
                )
            )
        if not options:
            return
        select_action = InputRequestAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = 1,
            must_select = False,  # Allow skipping if none of the options are desirable.
        )
        add_action(select_action, to_front=True)


@register("action")
class MarkRetainCardAction(Action):
    def __init__(self, card):
        self.card = card

    def execute(self) -> None:
        if self.card is not None:
            setattr(self.card, 'retain_this_turn', True)


@register("action")
class ChooseRetainCardAction(Action):
    def __init__(self, pile: str = 'hand', amount: int = 1):
        self.pile = pile
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        from actions.display import InputRequestAction

        options = []
        for card in game_state.player.card_manager.get_pile(self.pile):
            options.append(Option(name=card.info(), actions=[MarkRetainCardAction(card=card)]))
        if not options:
            return
        if len(options) <= self.amount:
            add_actions([action for option in options for action in option.actions], to_front=True)
            return
        add_action(InputRequestAction(title=LocalStr("ui.choose_cards_to_move"), options=options, max_select=self.amount, must_select=False), to_front=True)


@register("action")
class SetNightmarePowerAction(Action):
    def __init__(self, card):
        self.card = card

    def execute(self) -> None:
        from engine.game_state import game_state
        from powers.definitions.nightmare import NightmarePower
        if game_state.player is not None and self.card is not None:
            game_state.player.add_power(NightmarePower(owner=game_state.player, stored_card=self.card.copy()))


@register("action")
class ChooseNightmareCardAction(Action):
    def __init__(self, pile: str = 'hand'):
        self.pile = pile

    def execute(self) -> None:
        from engine.game_state import game_state
        if not game_state.player:
            return
        from actions.display import InputRequestAction

        options = []
        for card in game_state.player.card_manager.get_pile(self.pile):
            options.append(Option(name=card.info(), actions=[SetNightmarePowerAction(card=card)]))
        if not options:
            return
        if len(options) == 1:
            add_actions(options[0].actions, to_front=True)
            return
        add_action(InputRequestAction(title=LocalStr("ui.choose_cards_to_copy"), options=options, max_select=1, must_select=True), to_front=True)


@register("action")
class ChooseCardLambdaAction(Action):
    """Choose card(s) from a pile and build follow-up actions from the selection."""

    def __init__(
        self,
        pile: str = "hand",
        amount: int = 1,
        title: Optional[LocalStr] = None,
        must_select: bool = True,
        action_builder=None,
        filter_fn=None,
    ):
        self.pile = pile
        self.amount = amount
        self.title = title or LocalStr("ui.choose_cards_to_move")
        self.must_select = must_select
        self.action_builder = action_builder
        self.filter_fn = filter_fn

    def execute(self) -> None:
        from engine.game_state import game_state
        from actions.display import InputRequestAction

        if not game_state.player or self.action_builder is None:
            return

        options = []
        for card in game_state.player.card_manager.get_pile(self.pile):
            if self.filter_fn is not None and not self.filter_fn(card):
                continue
            built_actions = self.action_builder(card)
            if built_actions is None:
                continue
            if not isinstance(built_actions, list):
                built_actions = [built_actions]
            options.append(Option(name=card.info(), actions=built_actions))

        if not options:
            return
        if len(options) == 1 and self.amount == 1:
            add_actions(options[0].actions, to_front=True)
            return
        add_action(
            InputRequestAction(
                title=self.title,
                options=options,
                max_select=self.amount,
                must_select=self.must_select,
            ),
            to_front=True,
        )

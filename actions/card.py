from actions.base import Action
from typing import Optional, Union, List, TYPE_CHECKING
from actions.combat import ModifyMaxHpAction
from actions.display import SelectAction
from localization import LocalStr, t
from utils.option import Option
from utils.registry import register, get_registered, list_registered
from utils.types import CardType, PilePosType, RarityType
from utils.random import get_random_card, get_random_card_reward
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
    def __init__(self, card, dest_pile: str = None, source: str = None, position: PilePosType = PilePosType.TOP, chance: float = 1.0):
        self.card = card
        self.dest_pile = dest_pile
        self.source = source
        self.position = position
        self.chance = chance

    def execute(self) -> 'BaseResult':
        import random
        from engine.game_state import game_state
        from utils.types import CardType

        # Check probability if chance < 1.0
        if self.chance < 1.0 and random.random() >= self.chance:
            # Chance check failed - don't add the card
            return NoneResult()

        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                target_pile = self.dest_pile or "deck"
                follow_up_actions = []

                # Omamori: negate curse cards that would be added to deck.
                if (
                    target_pile in ("deck")
                    and getattr(self.card, "card_type", None) == CardType.CURSE
                ):
                    for relic in list(game_state.player.relics):
                        if getattr(relic, "idstr", None) != "Omamori":
                            continue
                        if not hasattr(relic, "try_negate_curse"):
                            continue
                        if relic.try_negate_curse():
                            if getattr(relic, "curses_to_negate", 0) <= 0:
                                game_state.player.relics.remove(relic)
                            print(
                                f"[Relic] Omamori negated curse: "
                                f"{self.card.display_name.resolve()}"
                            )
                            return NoneResult()

                # Egg relics: upgrade qualifying cards before adding to deck.
                if target_pile in ("deck"):
                    for relic in list(game_state.player.relics):
                        hook = getattr(relic, "should_upgrade_added_card", None)
                        if not hook:
                            continue
                        if hook(self.card, target_pile) and self.card.can_upgrade():
                            self.card.upgrade()

                game_state.player.card_manager.add_to_pile(self.card, target_pile, pos=self.position)
                # Ceramic Fish: whenever a card is added to deck, gain 9 gold.
                if target_pile in ("deck"):
                    from actions.reward import AddGoldAction
                    if any(
                        getattr(relic, "idstr", None) == "CeramicFish"
                        for relic in game_state.player.relics
                    ):
                        AddGoldAction(amount=9).execute()
                    for relic in list(game_state.player.relics):
                        hook = getattr(relic, "on_card_added", None)
                        if not hook:
                            continue
                        result = hook(self.card, target_pile)
                        if not result:
                            continue
                        if isinstance(result, list):
                            follow_up_actions.extend(result)
                        else:
                            follow_up_actions.append(result)
                # Only show [Reward] for actual rewards, use appropriate prefix for others
                # Localize pile name
                pile_name = t(f'combat.{target_pile}', default=target_pile)
                if self.source is None:
                    print(f"{t('action.card_added', default='Added')} {self.card.display_name.resolve()} {t('action.to_pile', default='to')} {pile_name}")
                elif self.source == "reward":
                    print(f"[{t('action.reward', default='Reward')}] {t('action.card_added', default='Added')} {self.card.display_name.resolve()} {t('action.to_pile', default='to')} {pile_name}")
                elif self.source == "enemy":
                    print(f"[{t('action.enemy', default='Enemy')}] {t('action.card_added', default='Added')} {self.card.display_name.resolve()} {t('action.to_pile', default='to')} {pile_name}")
                else:
                    print(f"[{self.source.title()}] {t('action.card_added', default='Added')} {self.card.display_name.resolve()} {t('action.to_pile', default='to')} {pile_name}")
                if follow_up_actions:
                    for action in follow_up_actions:
                        action.execute()
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
                if hasattr(relic, "on_card_exhaust"):
                    result = relic.on_card_exhaust(
                        card=self.card,
                        player=game_state.player,
                        entities=game_state.current_combat.enemies if game_state.current_combat else []
                    )
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
class RemoveAllStrikesAction(Action):
    """Remove all Strike cards from player's deck.

    Required:
        None

    Optional:
        None
    """
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from cards.ironclad.strike import Strike

        if not game_state.player:
            return NoneResult()

        removed_count = 0
        # Check all piles
        piles = ['draw_pile', 'hand', 'discard_pile', 'exhaust_pile']

        for pile_name in piles:
            if not hasattr(game_state.player, 'card_manager'):
                continue
            pile = getattr(game_state.player.card_manager, pile_name, None)
            if not pile:
                continue

            # Find all Strike cards in this pile
            strikes = [card for card in pile if isinstance(card, Strike)]
            for strike in strikes:
                game_state.player.card_manager.remove_from_pile(strike, pile_name)
                removed_count += 1

        print(f"[Event] Removed {removed_count} Strike card(s)")
        return NoneResult()


@register("action")
class RemoveRandomCardAction(Action):
    """Remove a random card of a specific type from player's deck.

    Required:
        card_type (CardType): Type of card to remove (SKILL, POWER, ATTACK)

    Optional:
        None
    """
    def __init__(self, card_type):
        self.card_type = card_type

    def execute(self) -> 'BaseResult':
        import random
        from engine.game_state import game_state
        from utils.types import CardType

        if not game_state.player or not hasattr(game_state.player, 'card_manager'):
            return NoneResult()

        # Get all cards from all piles
        all_cards = []
        card_manager = game_state.player.card_manager

        # Map card_type string to actual CardType enum if needed
        target_type = self.card_type
        if isinstance(target_type, str):
            type_map = {
                'skill': CardType.SKILL,
                'power': CardType.POWER,
                'attack': CardType.ATTACK
            }
            target_type = type_map.get(target_type.lower())

        # Check each pile for matching cards
        piles = ['draw_pile', 'hand', 'discard_pile', 'exhaust_pile']
        for pile_name in piles:
            pile = getattr(card_manager, pile_name, [])
            for card in pile:
                if hasattr(card, 'card_type') and card.card_type == target_type:
                    all_cards.append((card, pile_name))

        if not all_cards:
            print(f"[Event] No {self.card_type} cards found to remove")
            return NoneResult()

        # Remove a random card
        card_to_remove, pile_name = random.choice(all_cards)
        card_manager.remove_from_pile(card_to_remove, pile_name)
        print(f"[Event] Removed {card_to_remove.name} ({self.card_type})")

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
        
    def execute(self) -> BaseResult:
        from engine.game_state import game_state
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

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
            return NoneResult()
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_remove"),
            options = options,
            max_select = self.amount,
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
            return NoneResult()
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
            
            # 创建副本并升级，以获取升级后的信息
            upgraded_card = card.copy()
            upgraded_card.upgrade()
            
            # 构建简洁的升级预览：卡牌名 + 升级前费用（升级后费用） + 升级前描述 -> 升级后描述
            from localization import ConcatLocalStr
            from utils.dynamic_values import resolve_card_value
            
            # 获取费用
            before_cost = resolve_card_value(card, 'cost')
            after_cost = resolve_card_value(upgraded_card, 'cost')
            
            # 获取描述
            before_desc = card.description.resolve() if hasattr(card, 'description') else ""
            after_desc = upgraded_card.description.resolve() if hasattr(upgraded_card, 'description') else ""
            
            # 构建简洁的升级预览
            cost_display = f"{before_cost}"
            if before_cost != after_cost:
                cost_display = f"{before_cost}→{after_cost}"
            
            # 如果描述相同，只显示一次
            if before_desc == after_desc:
                option = ConcatLocalStr(
                    card.display_name,
                    f" ({cost_display}) {before_desc}"
                )
            else:
                option = ConcatLocalStr(
                    card.display_name,
                    f" ({cost_display}) {before_desc} → {after_desc}"
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
            return NoneResult()
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
            return NoneResult()
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
            # * 设置临时能量
            if self.temp_cost is not None:
                random_card.temp_cost = self.temp_cost
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
            return NoneResult()
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

        if random_card is None:
            return NoneResult()
        
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
            return NoneResult()
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
        position (PilePosType): Position in destination pile (TOP or BOTTOM), default TOP
    """
    def __init__(self, src: str, dst: str, amount: int = 1, filter_card_type: Optional[CardType] = None, position: PilePosType = PilePosType.TOP):
        self.src = src
        self.dst = dst
        self.amount = amount
        self.filter_card_type = filter_card_type
        self.position = position

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
            return NoneResult()
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
        card_types (List[CardType]): List of allowed card types. If None, all types are allowed.
    """
    def __init__(self, pile: str = 'hand', copies: int = 1, card_types: Optional[List['CardType']] = None):
        self.pile = pile
        self.copies = copies
        self.card_types = card_types

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        pile = self.pile
        copies = self.copies
        card_types = self.card_types

        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

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
            return NoneResult()
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
        position (PilePosType): Position in destination pile (TOP or BOTTOM), default TOP
    """
    def __init__(self, card, src_pile: str, dst_pile: str, position: PilePosType = PilePosType.TOP):
        self.card = card
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.position = position

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                game_state.player.card_manager.add_to_pile(self.card, self.dst_pile, pos=self.position)
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
class SetTempCostAction(Action):
    """Set temporary cost for a card (resets at end of turn)

    Required:
        card (Card): Card to modify
        temp_cost (int): Temporary cost value (None to reset)

    Optional:
        None
    """
    def __init__(self, card: "Card", temp_cost: Optional[int]):
        self.card = card
        self.temp_cost = temp_cost

    def execute(self) -> 'BaseResult':
        if self.card:
            self.card.temp_cost = self.temp_cost
        return NoneResult()


@register("action")
class MoveAndSetCostAction(Action):
    """Move a card and set its temporary cost to 0.
    
    Used by Forethought card: move card to bottom of draw pile, 
    and set its cost to 0 until played.

    Required:
        card (Card): Card to move
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name
        temp_cost (int): Temporary cost to set (default 0)

    Optional:
        position (PilePosType): Position in destination pile (default BOTTOM)
    """
    def __init__(self, card: "Card", src_pile: str, dst_pile: str, 
                 temp_cost: int = 0, position: PilePosType = PilePosType.BOTTOM):
        self.card = card
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.temp_cost = temp_cost
        self.position = position

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if self.card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                # Move the card
                game_state.player.card_manager.remove_from_pile(self.card, self.src_pile)
                game_state.player.card_manager.add_to_pile(self.card, self.dst_pile, pos=self.position)
                # Set temporary cost
                self.card.temp_cost = self.temp_cost
        return NoneResult()

@register("action")
class ChooseMoveAndSetCostAction(Action):
    """Choose cards to move and set their temporary cost.
    
    Used by Forethought card: choose cards from hand, move to bottom 
    of draw pile, and set their cost to 0 until played.

    Required:
        src_pile (str): Source pile name
        dst_pile (str): Destination pile name
        amount (int): Number of cards to choose (-1 for any number)
        temp_cost (int): Temporary cost to set (default 0)

    Optional:
        position (PilePosType): Position in destination pile (default BOTTOM)
        must_select (bool): Whether selection is required (default True)
    """
    def __init__(self, src_pile: str, dst_pile: str, amount: int = 1, 
                 temp_cost: int = 0, position: PilePosType = PilePosType.BOTTOM,
                 must_select: bool = True):
        self.src_pile = src_pile
        self.dst_pile = dst_pile
        self.amount = amount
        self.temp_cost = temp_cost
        self.position = position
        self.must_select = must_select

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

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
                            temp_cost=self.temp_cost,
                            position=self.position
                        ),
                    ]
                )
            )

        if not options:
            return NoneResult()
        
        # amount = -1 means any number of cards
        max_select = self.amount if self.amount > 0 else len(cards_in_pile)
        
        select_action = SelectAction(
            title=LocalStr("ui.choose_cards_to_set_cost"),
            options=options,
            max_select=max_select,
            must_select=self.must_select
        )
        return SingleActionResult(select_action)


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
class UpgradeAllCardsAction(Action):
    """Upgrade all cards in player's deck.

    Required:
        None

    Optional:
        None
    """

    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        deck = game_state.player.card_manager.get_pile('deck')

        upgraded_count = 0
        for card in deck:
            if card.can_upgrade():
                card.upgrade()
                upgraded_count += 1

        if upgraded_count > 0:
            print(f"[Event] Upgraded {upgraded_count} card(s)")

        return NoneResult()


@register("action")
class UpgradeRandomCardAction(Action):
    """Upgrade a random card from player's deck.

    Required:
        count (int): Number of cards to upgrade

    Optional:
        card_type (str): Type of cards to choose from (Attack/Skill/Power)
        namespace (str): Card namespace (default: player's character)
    """
    def __init__(self, count: int = 1, card_type: Optional[str] = None, 
                 namespace: Optional[str] = None):
        self.count = count
        self.card_type = card_type
        self.namespace = namespace
    
    def execute(self) -> 'BaseResult':
        """Execute: upgrade random cards from deck"""
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
        
        # Randomly select cards to upgrade
        import random
        cards_to_upgrade = random.sample(cards_to_choose, actual_count)
        
        # Create upgrade actions for all selected cards
        actions = []
        for card in cards_to_upgrade:
            actions.append(UpgradeCardAction(card=card))
        
        if len(actions) == 1:
            return SingleActionResult(actions[0])
        else:
            return MultipleActionsResult(actions)


@register("action")
class TransformRandomCardAction(Action):
    """Transform a random card from player's deck.

    Required:
        count (int): Number of cards to transform

    Optional:
        card_type (str): Type of cards to choose from (Attack/Skill/Power)
    """
    def __init__(self, count: int = 1, card_type: Optional[str] = None):
        self.count = count
        self.card_type = card_type

    def execute(self) -> 'BaseResult':
        """Execute: transform random cards from deck"""
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        from utils.types import CardType

        # Get deck
        deck = game_state.player.card_manager.get_pile('deck')

        if not deck:
            return NoneResult()

        # Filter cards by type (if specified)
        cards_to_choose = []
        for card in deck:
            if self.card_type is not None:
                # Match card type
                if self.card_type == "Attack" and card.card_type != CardType.ATTACK:
                    continue
                elif self.card_type == "Skill" and card.card_type != CardType.SKILL:
                    continue
                elif self.card_type == "Power" and card.card_type != CardType.POWER:
                    continue

            cards_to_choose.append(card)

        if not cards_to_choose:
            print(t("ui.no_cards_to_transform", default="No cards to transform found"))
            return NoneResult()

        # If requesting more than available, reduce to available
        actual_count = min(self.count, len(cards_to_choose))

        # Randomly select cards to transform
        import random
        cards_to_transform = random.sample(cards_to_choose, actual_count)

        # Create transform actions for all selected cards
        actions = []
        for card in cards_to_transform:
            actions.append(TransformCardAction(card=card, pile='deck'))

        if len(actions) == 1:
            return SingleActionResult(actions[0])
        else:
            return MultipleActionsResult(actions)


@register("action")
class TransformAndUpgradeCardAction(Action):
    """Transform a card and upgrade the new card.
    
    Used by Astrolabe relic.
    
    Required:
        card (Card): Card to transform
        pile (str): Card location
        
    Optional:
        None
    """
    def __init__(self, card, pile: str):
        self.card = card
        self.pile = pile
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state

        if not game_state.player:
            return NoneResult()

        namespace = self.card.namespace
        
        # Get a random card from the same namespace
        new_card = get_random_card(namespaces=[namespace])
        
        if new_card is None:
            return NoneResult()
        
        # Upgrade the new card before adding
        if new_card.can_upgrade():
            new_card.upgrade()
        
        # Return actions: remove old card, add upgraded new card
        return MultipleActionsResult([
            RemoveCardAction(card=self.card, src_pile=self.pile),
            AddCardAction(card=new_card, dest_pile=self.pile),
        ])


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
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        from actions.combat import ModifyMaxHpAction
        if not game_state.player:
            return NoneResult()
        pile = self.pile
        amount = self.amount
        
        card_manager = game_state.player.card_manager
        from actions.display import SelectAction

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
            return NoneResult()
        select_action = SelectAction(
            title = LocalStr("ui.choose_cards_to_transform_and_upgrade"),
            options = options,
            max_select = amount,
            must_select = True
        )
        return SingleActionResult(select_action)


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
    
    def execute(self) -> 'BaseResult':
        from engine.game_state import game_state
        if not game_state.player:
            return NoneResult()

        from actions.display import SelectAction

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
            and hasattr(relic, "can_choose_max_hp_instead_of_card")
            and relic.can_choose_max_hp_instead_of_card()
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
            return NoneResult()
        select_action = SelectAction(
            title = LocalStr("ui.choose_random_card_to_add"),
            options = options,
            max_select = 1,
            must_select = False, # ? 是否全部都是，可以跳过
        )
        return SingleActionResult(select_action)   

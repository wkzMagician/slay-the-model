from actions.base import Action
from utils.registry import register

@register("action")
class CreateRandomCardAction(Action):
    """Create a random card and add to deck
    
    Required:
        None
        
    Optional:
        location (str): Card location ('deck' or 'hand')
    """
    REQUIRED_PARAMS = {}
    OPTIONAL_PARAMS = {
        "location": (str, "deck"),
    }
    
    def execute(self):
        from engine.game_state import game_state
        location = self.kwargs.get('location', 'deck')

        if not game_state.player:
            return

        # Generate a random card
        import random
        from cards.namespaces import CARD_NAMESPACES
        all_cards = []
        for namespace in CARD_NAMESPACES.values():
            all_cards.extend(namespace.keys())

        if all_cards:
            card_id = random.choice(all_cards)
            if location == 'deck':
                game_state.player.card_manager.add_to_deck(card_id)
            from cards.registry import create_card
            card = create_card(card_id)
            from localization import t
            print(t("ui.received_card", default=f"Received card: {card.name if card else card_id}!", name=card.name if card else card_id))
         
@register("action")   
class ChooseRemoveCardAction(Action):
    """Choose a card to remove from hand
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to remove
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "pile": str,
        "amount": int,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.kwargs.get('pile', 'hand')
        amount = self.kwargs.get('amount', 1)
        if pile == 'hand':
            game_state.player.card_manager.remove(amount, location='hand')
        elif pile == 'deck':
            game_state.player.card_manager.remove(amount, location='deck')
            
        from localization import t
        print(t("ui.removed_cards", default=f"Removed {amount} cards from {pile}!", amount=amount, pile=pile))

@register("action")         
class ChooseTransformCardAction(Action):
    """Choose a card to transform
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to transform
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "pile": str,
        "amount": int,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.kwargs.get('pile', 'hand')
        amount = self.kwargs.get('amount', 1)
        if pile == 'hand':
            game_state.player.card_manager.transform(amount, location='hand')
        elif pile == 'deck':
            game_state.player.card_manager.transform(amount, location='deck')
            
        from localization import t
        print(t("ui.transformed_cards", default=f"Transformed {amount} cards from {pile}!", amount=amount, pile=pile))
      
@register("action")     
class ChooseUpgradeCardAction(Action):
    """Choose a card to upgrade
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        amount (int): Amount of cards to upgrade
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "pile": str,
        "amount": int,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.kwargs.get('pile', 'hand')
        amount = self.kwargs.get('amount', 1)
        if pile == 'hand':
            game_state.player.card_manager.upgrade(amount, location='hand')
        elif pile == 'deck':
            game_state.player.card_manager.upgrade(amount, location='deck')
            
        from localization import t
        print(t("ui.upgraded_cards", default=f"Upgraded {amount} cards from {pile}!", amount=amount, pile=pile))
     
@register("action")      
class ChooseCardAction(Action):
    """Choose a card to obtain
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        total (int): Total amount of cards to obtain
        card_type (str): Card type
        rarity (str): Card rarity
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "pile": str,
        "total": int,
        "card_type": str,
        "rarity": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.kwargs.get('pile', 'hand')
        total = self.kwargs.get('total', 1)
        card_type = self.kwargs.get('card_type', None)
        rarity = self.kwargs.get('rarity', None)
        if pile == 'hand':
            game_state.player.card_manager.obtain(total, card_type, rarity, location='hand')
        elif pile == 'deck':
            game_state.player.card_manager.obtain(total, card_type, rarity, location='deck')
            
        from localization import t
        print(t("ui.obtained_cards", default=f"Obtained {total} cards from {pile}!", total=total, pile=pile))       
        
@register("action")   
class ObtainRandomCardAction(Action):
    """Obtain a random card
    
    Required:
        pile (str): Card location ('deck' or 'hand')
        card_type (str): Card type
        rarity (str): Card rarity
        
    Optional:
        None
    """
    REQUIRED_PARAMS = {
        "pile": str,
        "card_type": str,
        "rarity": str,
    }
    OPTIONAL_PARAMS = {}
    
    def execute(self):
        from engine.game_state import game_state
        if not game_state.player:
            return
        pile = self.kwargs.get('pile', 'hand')
        card_type = self.kwargs.get('card_type', None)
        rarity = self.kwargs.get('rarity', None)
        if pile == 'hand':
            game_state.player.card_manager.obtain(1, card_type, rarity, location='hand')
            
@register("action")
class RemoveCardAction(Action):
    """Choose a card to remove from hand
    
    Required:
        card (Card): Card to remove
        
    Optional:
        reason (str): Removal reason (for UI / logging)
    """
    REQUIRED_PARAMS = {
        "card": None,  # Card type, use None to skip type checking
    }
    OPTIONAL_PARAMS = {
        "reason": (str, None),
    }
    
    def execute(self):
        from engine.game_state import game_state
        card = self.kwargs.get('card', None)
        if card and game_state.player:
            if hasattr(game_state.player, "card_manager"):
                game_state.player.card_manager.remove_from_deck(card)


@register("action")
class ExhaustCardAction(Action):
    """Exhaust a card into exhaust pile.

    Required:
        card (Card): Card to exhaust

    Optional:
        source_pile (str): Source pile name
    """
    REQUIRED_PARAMS = {
        "card": None,
    }
    OPTIONAL_PARAMS = {
        "source_pile": (str, None),
    }

    def execute(self):
        from engine.game_state import game_state
        card = self.kwargs.get("card")
        source_pile = self.kwargs.get("source_pile")
        if card and game_state.player and hasattr(game_state.player, "card_manager"):
            return game_state.player.card_manager.exhaust(card, source_pile=source_pile)
        return False
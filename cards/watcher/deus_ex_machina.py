from actions.card import AddCardAction
from actions.card_lifecycle import ExhaustCardAction
from cards.base import COST_UNPLAYABLE, Card
from engine.runtime_api import add_action
from utils.registry import register
from utils.types import CardType, RarityType, TargetType

@register("card")
class DeusExMachina(Card):
    card_type = CardType.SKILL
    target_type = TargetType.SELF
    rarity = RarityType.RARE
    base_cost = COST_UNPLAYABLE
    base_exhaust = True
    base_magic = {"count": 2}
    upgrade_magic = {"count": 3}
    text_name = "Deus Ex Machina"
    text_description = "Unplayable. When drawn, add {magic.count} Miracles to your hand. Exhaust."

    def on_draw(self):
        from cards.colorless.miracle import Miracle

        for _ in range(self.get_magic_value("count")):
            add_action(AddCardAction(Miracle(), dest_pile="hand"))
        add_action(ExhaustCardAction(self, source_pile="hand"))

from cards.watcher._base import *

@register("card")
class Omniscience(WatcherSkill):
    rarity = RarityType.RARE
    base_cost = 4
    upgrade_cost = 3
    base_exhaust = True
    text_name = "Omniscience"
    text_description = "Choose a card in your hand. Play it twice. Exhaust."

    def on_play(self, targets: List = []):
        options = []
        for card in list(_player().card_manager.get_pile("hand")):
            if card is self:
                continue
            options.append(
                Option(
                    name=card.info(),
                    actions=[PlayCardAction(card, ignore_energy=True), PlayCardAction(card, ignore_energy=True)],
                )
            )
        if options:
            add_action(InputRequestAction(title=RawLocalStr("Choose a card to play twice"), options=options))

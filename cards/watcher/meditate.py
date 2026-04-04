from cards.watcher._base import *

@register("card")
class Meditate(WatcherSkill):
    rarity = RarityType.UNCOMMON
    base_cost = 1
    base_magic = {"pick": 1}
    upgrade_magic = {"pick": 2}
    base_exhaust = True
    text_name = "Meditate"
    text_description = "Put up to {magic.pick} cards from your discard pile into your hand. Enter Calm. Exhaust."

    def on_play(self, targets: List = []):
        add_action(ChangeStanceAction(StatusType.CALM))
        add_action(
            ChooseCardLambdaAction(
                pile="discard_pile",
                amount=self.get_magic_value("pick"),
                must_select=False,
                action_builder=lambda card: MoveCardAction(card=card, src_pile="discard_pile", dst_pile="hand"),
            )
        )

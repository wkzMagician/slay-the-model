"""
Neo blessing event.
"""
from events.event_pool import register_event
from actions.card import ChooseAddRandomCardAction, ChooseRemoveCardAction, ChooseTransformCardAction, ChooseUpgradeCardAction, AddRandomCardAction
from actions.display import SelectAction
from actions.reward import AddGoldAction, AddRandomPotionAction, AddRandomRelicAction, AddRelicAction, LoseGoldAction, LoseRelicAction
from actions.combat import LoseHpAction, ModifyMaxHpAction
from engine.game_state import game_state
from engine.game_stats import game_stats
from events.base_event import Event
from localization import LocalStr
from utils.option import Option
from utils.types import CardType, RarityType


@register_event(
    event_id="neo_blessing",
    floors='all',
    weight=0,  # Neo event is special, never randomly selected
    is_unique=False
)
class NeoEvent(Event):
    """Neo blessing event - special starting event"""

    def trigger(self) -> str:
        """Trigger Neo blessing selection"""
        # Display welcome message
        from actions.display import DisplayTextAction
        self.action_queue.add_action(DisplayTextAction(
            text_key="events.neo.welcome"
        ))
        
        # Check if player has reached boss before
        if game_state.run_history.get("reached_exordium_boss", False):
            self._show_four_blessings()
        else:
            self._show_basic_blessings()
        
        # Execute actions
        result = self.execute_actions()
        
        # End event after selection
        self.end_event()
        
        return result
    
    def _show_basic_blessings(self):
        """Show basic blessing options (first run)"""
        max_hp_small_increase = game_stats.neow_max_hp_small_increases.get(game_state.player.character, 0)
        
        options = [
            Option(
                name=LocalStr("blessing.max_hp_option"),
                actions=[ModifyMaxHpAction(amount=max_hp_small_increase)]
            ),
            Option(
                name=LocalStr("blessing.random_common_relic_option"),
                actions=[AddRelicAction(relic="Neow's Blessing")]
            )
        ]
        
        self.action_queue.add_action(
            SelectAction(
                title=LocalStr("ui.choose_blessings"),
                options=options
            )
        )
    
    def _show_four_blessings(self):
        """Show advanced blessing options (after reaching boss)"""
        max_hp_small_increase = game_stats.neow_max_hp_small_increases.get(game_state.player.character, 0)
        max_hp_large_increase = game_stats.neow_max_hp_large_increases.get(game_state.player.character, 0)
        max_hp_small_decrease = game_stats.neow_max_hp_small_decreases.get(game_state.player.character, 0)
        damage_taken = (game_state.player.hp // 10) * 3
        
        # Card blessings
        card_blessings = [
            Option(
                name=LocalStr("blessing.remove_card_option"),
                actions=[ChooseRemoveCardAction(pile="deck", amount=1)]
            ),
            Option(
                name=LocalStr("blessing.transform_card_option"),
                actions=[ChooseTransformCardAction(pile="deck", amount=1)]
            ),
            Option(
                name=LocalStr("blessing.upgrade_card_option"),
                actions=[ChooseUpgradeCardAction(pile="deck", amount=1)]
            ),
            Option(
                name=LocalStr("blessing.choose_card_option"),
                actions=[ChooseAddRandomCardAction(pile="deck", total=3, namespace=game_state.player.character, rarity=None)]
            ),
            Option(
                name=LocalStr("blessing.uncommon_colorless_option"),
                actions=[ChooseAddRandomCardAction(pile="deck", total=3, namespace="colorless", rarity=RarityType.UNCOMMON)]
            ),
            Option(
                name=LocalStr("blessing.random_rare_card_option"),
                actions=[AddRandomCardAction(pile="deck", namespace=game_state.player.character, rarity=RarityType.RARE)]
            )
        ]
        
        # Non-card blessings
        non_card_blessings = [
            Option(
                name=LocalStr("blessing.max_hp_option"),
                actions=[ModifyMaxHpAction(amount=max_hp_small_increase)]
            ),
            Option(
                name=LocalStr("blessing.neow_option"),
                actions=[AddRelicAction(relic="Neow's Blessing")]
            ),
            Option(
                name=LocalStr("blessing.random_common_relic_option"),
                actions=[AddRandomRelicAction(rarities=[RarityType.COMMON])]
            ),
            Option(
                name=LocalStr("blessing.receive_100_gold_option"),
                actions=[AddGoldAction(amount=100)]
            ),
            Option(
                name=LocalStr("blessing.three_random_potions_option"),
                actions=[
                    AddRandomPotionAction(character=game_state.player.character),
                    AddRandomPotionAction(character=game_state.player.character)
                ]
            )
        ]
        
        # Disadvantage blessings
        disadvantage_blessings = [
            Option(
                name=LocalStr("blessing.lose_max_hp_option"),
                actions=[ModifyMaxHpAction(amount=-max_hp_small_decrease)]
            ),
            Option(
                name=LocalStr("blessing.take_damage_option"),
                actions=[LoseHpAction(amount=damage_taken)]
            ),
            Option(
                name=LocalStr("blessing.obtain_curse_option"),
                actions=[AddRandomCardAction(pile="deck", card_type=CardType.CURSE, rarity=None)]
            ),
            Option(
                name=LocalStr("blessing.lose_all_gold_option"),
                actions=[LoseGoldAction(amount=game_state.player.gold)]
            )
        ]
        
        # Advantage blessings
        advantage_blessings = [
            Option(
                name=LocalStr("blessing.remove_two_cards_option"),
                actions=[ChooseRemoveCardAction(pile="deck", amount=2)]
            ),
            Option(
                name=LocalStr("blessing.transform_two_cards_option"),
                actions=[ChooseTransformCardAction(pile="deck", amount=2)]
            ),
            Option(
                name=LocalStr("blessing.gain_250_gold_option"),
                actions=[AddGoldAction(amount=250)]
            ),
            Option(
                name=LocalStr("blessing.choose_rare_card_option"),
                actions=[ChooseAddRandomCardAction(pile="deck", total=3, namespace=game_state.player.character, rarity=RarityType.RARE)]
            ),
            Option(
                name=LocalStr("blessing.choose_rare_colorless_card_option"),
                actions=[ChooseAddRandomCardAction(pile="deck", total=3, namespace="colorless", rarity=RarityType.RARE)]
            ),
            Option(
                name=LocalStr("blessing.random_rare_relic_option"),
                actions=[AddRandomRelicAction(rarities=[RarityType.RARE])]
            ),
            Option(
                name=LocalStr("blessing.big_max_hp_option"),
                actions=[ModifyMaxHpAction(amount=max_hp_large_increase)]
            )
        ]
        
        import random
        
        # Randomly select one from each category
        card_blessing = random.choice(card_blessings)
        non_card_blessing = random.choice(non_card_blessings)
        disadvantage_blessing = random.choice(disadvantage_blessings)
        advantage_blessing = random.choice(advantage_blessings)
        
        # Mixed blessing (disadvantage + advantage)
        mixed_blessing = Option(
            name=disadvantage_blessing.name + advantage_blessing.name,
            actions=disadvantage_blessing.actions + advantage_blessing.actions
        )
        
        # Relic blessing
        if game_state.player.relics:
            relic_blessing = Option(
                name=LocalStr("blessing.replace_starter_relic_option"),
                actions=[
                    LoseRelicAction(relic=game_state.player.relics[0]),
                    AddRandomRelicAction(rarities=[RarityType.BOSS])
                ]
            )
            options = [card_blessing, non_card_blessing, mixed_blessing, relic_blessing]
        else:
            options = [card_blessing, non_card_blessing, mixed_blessing]
        
        self.action_queue.add_action(
            SelectAction(
                title=LocalStr("ui.choose_blessings"),
                options=options
            )
        )
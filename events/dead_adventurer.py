"""Event: Dead Adventurer - Act 1 Event (Floor 7+)

A risk/reward event where you search for loot with increasing chance of elite ambush.
Elite encounter probability: 0% -> 25% -> 50% -> 75% per search (A15+: 10% -> 35% -> 60% -> 85%)
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

import random
from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from actions.base import LambdaAction
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType
from engine.game_state import game_state


@register_event(category='event', event_id='dead_adventurer', acts=[1], weight=100)
class DeadAdventurer(Event):
    """Dead Adventurer - search for loot with elite risk."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ within Act 1."""
        return game_state.floor_in_act >= 7
    
    def __init__(self):
        super().__init__()
        self.search_count = 0
        self.found_gold = False
        self.found_relic = False
        self.found_nothing = False
        self.elite_type = random.choice(['gremlin_nob', 'lagavulin', 'sentries'])
    
    def _get_elite_chance(self) -> int:
        """Get elite encounter chance based on search count."""
        base_chances = [0, 25, 50, 75]
        if game_state.ascension >= 15:
            base_chances = [10, 35, 60, 85]
        return base_chances[min(self.search_count, 3)]
    
    def _get_elite_enemies(self) -> list:
        """Build the event encounter using actual classes and position-aware factories."""
        from enemies.act1.gremlin_nob import GremlinNob
        from enemies.act1.lagavulin import Lagavulin
        from map.encounter_pool import _create_sentries

        if self.elite_type == "gremlin_nob":
            return [GremlinNob()]
        if self.elite_type == "lagavulin":
            return [Lagavulin(start_awake=True)]
        if self.elite_type == "sentries":
            return _create_sentries()
        raise ValueError(f"Unknown Dead Adventurer encounter: {self.elite_type}")

    def _get_search_reward_actions(self) -> list:
        """Get random reward actions from remaining rewards."""
        available_rewards = []
        
        if not self.found_gold:
            available_rewards.append('gold')
        if not self.found_relic:
            available_rewards.append('relic')
        if not self.found_nothing:
            available_rewards.append('nothing')
        
        if not available_rewards:
            return [DisplayTextAction(text_key='events.dead_adventurer.nothing')]
        
        reward = random.choice(available_rewards)
        actions = []
        
        if reward == 'gold':
            self.found_gold = True
            actions.append(AddGoldAction(amount=30))
        elif reward == 'relic':
            self.found_relic = True
            actions.append(AddRandomRelicAction(
                rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]
            ))
        else:
            self.found_nothing = True
            actions.append(DisplayTextAction(text_key='events.dead_adventurer.nothing'))
        
        return actions

    def _count_search(self) -> None:
        self.search_count += 1
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.dead_adventurer.description'
        ))
        
        # Build options
        options = []
        
        # Option to continue searching (max 3 times)
        if self.search_count < 3:
            elite_chance = self._get_elite_chance()
            
            if random.randint(1, 100) <= elite_chance:
                # Elite encounter - fight with rewards on victory
                elite_enemies = self._get_elite_enemies()
                
                # Build victory rewards: remaining loot + bonus gold
                victory_rewards = []
                if not self.found_gold:
                    victory_rewards.append(AddGoldAction(amount=30))
                if not self.found_relic:
                    victory_rewards.append(AddRandomRelicAction(
                        rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]
                    ))
                victory_rewards.append(AddGoldAction(amount=random.randint(25, 35)))
                victory_rewards.append(LambdaAction(lambda: self.end_event()))
                
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    detail=LocalStr('events.dead_adventurer.search_detail', chance=elite_chance),
                    actions=[
                        DisplayTextAction(text_key='events.dead_adventurer.elite_appears'),
                        LambdaAction(self._count_search),
                        StartFightAction(
                            enemies=elite_enemies,
                            escape_actions=[LambdaAction(self.end_event)],
                            victory_actions=victory_rewards
                        )
                    ]
                ))
            else:
                # No elite - give random reward
                search_actions = self._get_search_reward_actions()
                options.append(Option(
                    name=LocalStr('events.dead_adventurer.search'),
                    detail=LocalStr('events.dead_adventurer.search_detail', chance=elite_chance),
                    actions=[
                        *search_actions,
                        LambdaAction(self._count_search),
                        LambdaAction(self.trigger),
                    ]
                ))
        
        # Leave option
        options.append(Option(
            name=LocalStr('events.dead_adventurer.leave'),
            detail=LocalStr('events.no_effect'),
            actions=[LambdaAction(lambda: self.end_event())]
        ))
        
        actions.append(InputRequestAction(
            title=LocalStr('events.dead_adventurer.title'),
            options=options
        ))
        
        add_actions(actions)

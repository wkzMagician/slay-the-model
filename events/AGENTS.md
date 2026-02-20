# EVENTS MODULE - AGENTS.md

## OVERVIEW
Random event system with 60+ events. Choices, requirements, effects. No UI.

## KEY CLASSES
- `Event`: Base class for all random events
- `Choice`: Represents a single choice option with requirements/effects

## PATTERNS
- Events contain `choices` array
- Each choice has `requirements` and `effects`
- Effects: give gold/cards/relics/potions, HP changes
- Some events require specific conditions (gold amount, HP threshold)

## EVENT TYPES
- Combat: Fight special enemies with unique rewards
- Reward: Free gold/cards/relics with no downside
- Risk/Reward: Lose something to gain something
- Transform: Upgrade/remove/transform cards

## ADDING EVENTS
- Create `events/{event_name}.py`
- Inherit from `Event` class
- Define `choices` array with requirement/effect logic
- Add localization strings to `localization/{en,zh}/`

## ANTI-PATTERNS
- NO bypassing event requirements without checking
- NO events that only give positive outcomes (always some cost/risk)
- NO hardcoded text - use localization system
- NO modifying player state outside effect functions

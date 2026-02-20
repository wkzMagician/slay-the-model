# POWERS MODULE

Power/buff/debuff system with 50+ power definitions.

## KEY CLASSES

Power - Base class for all powers
ApplyPowerAction - Action to apply/remove powers

## PATTERNS

- @register decorator auto-registers powers
- Powers have stacks (int) for intensity
- Buffs (positive) and debuffs (negative)
- at_start_of_turn(), at_end_of_turn() hooks
- modify_damage(), modify_block() hooks

## COMMON POWERS

Strength: +damage per stack
Dexterity: +block per stack
Poison: Damage per turn
Vulnerable: +50% damage taken
Weak: -25% damage dealt

## ANTI-PATTERNS

- NO skipping @register decorator
- NO direct power application - use ApplyPowerAction
- NO modifying stacks directly - use modify_stacks()

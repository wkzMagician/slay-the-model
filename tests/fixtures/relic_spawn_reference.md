# Fixed-JAR relic spawn reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
The deterministic gzip fixture contains 1824 prepared component cases across
four roles and A0/A20. Of these, 1736 invoke the actual original relic classes'
canSpawn methods and 88 execute original key/tail/non-campfire draw helpers.

The driver is RelicSpawnReference.java and reuses RewardReference.java and
ContentPoolReference.java. Compile all three with JDK17 and the fixed JAR on
the classpath. Run RelicSpawnReference with four arguments, the absolute paths
to relic_catalog_reference.json, special_card_catalog.json, an input JSON array,
and an output JSON. The checked-in gzip rows are valid replay inputs. Output
fields allowed/result/after/calls/state are overwritten by the driver.
Run in a temporary directory to contain original display/log bookkeeping.

The driver uses Unsafe to prepare the player, rooms, and actual relic instances.
Localization strings are placeholders. Permanent cards use original type and
rarity metadata. The 35 catalog relics with canSpawn overrides use their actual
original implementation. Other pool entries use metadata doubles. Campfire
makeCopy runs original constructors under the headless setup. Endless mode is
false. Floors, acts, decks, upgrades, held relics and ordered pools are explicit
inputs. They cover floor boundaries, shop exclusions, all campfire combinations,
bottle eligibility, Ectoplasm and starter-replacement controls.

Python tests call real production can_spawn and draw paths. Non-campfire cases
fix the outer tier roll to RARE because the original component receives an
already selected tier. A separate regression checks that the elite action rolls
only once. Each case compares eligibility or result and remaining pools, plus
the relic RNG counter and XS128 state. Original components consume no RNG for
these inputs. This evidence covers the prepared components. Full game lifecycle,
partial unlocks, and complete same-seed runs have separate acceptance records.

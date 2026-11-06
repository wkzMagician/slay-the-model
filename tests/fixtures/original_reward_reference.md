Fixed original: Slay the Spire V2.3.4 (2022-12-18), desktop-1.0.jar,
SHA-256 `cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

`original_reward_reference.json` contains 576 actual calls to that JAR's
`AbstractDungeon.getRewardCards`, `rollRarity`, `CardGroup.getRandomCard`, and RNG.
Each row records candidates/upgrades, every integer/upgrade Boolean call, the
compensation offset and final XS128 state/counter. Inputs cover four role pools,
seeds 0/1/42/-1, offsets +5/0/-40, acts 1/2/3, A0/A12, normal/elite rooms.

`card_pool_reference.json` is the pre-repair 2026-10-29 reference, reconstructed
from fixed-source CardLibrary registration and actual JDK8/17 HashMap iteration.
It supplies current and reversed source pools. This is not an actual game
CardLibrary initialization dump. The repair does not generate its own expected
pool order.

Reproduction with JDK17 and the fixed original JAR:

```
javac -encoding UTF-8 -cp ORIGINAL_JAR -d TEMP_CLASSES tests/reference/RewardReference.java
java -cp TEMP_CLASSES;ORIGINAL_JAR RewardReference tests/fixtures/card_pool_reference.json OUTPUT_JSON
```

Quote the classpath on Windows. Run in an isolated working directory using
absolute input/output paths: the JAR initializes display/log bookkeeping there.

The driver prepares localization, graphics/file/font/preferences placeholders
only to let static initialization finish without a game window. It allocates
metadata-only card doubles, overriding copying/canUpgrade/upgrade/use, and an
Ironclad player shell with no relics. Pool IDs and rarities come from the older
pool reference. The original reward selection, rejection, RNG and room rarity
methods execute unchanged; tracing delegates every RNG result to the original.
This validates the reward algorithm, not real card effects, relic lifecycles,
locked profiles, Prismatic Shard, or a complete original game session.

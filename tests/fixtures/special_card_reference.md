The reference uses the fixed Slay the Spire V2.3.4 desktop-1.0.jar.
Its SHA-256 is `cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

The driver is `tests/reference/SpecialCardReference.java`. It reuses the
headless initialization and prepared metadata-card doubles in RewardReference.
The metadata input comes from the pre-repair 2026-10-29 source catalog and
HEALING tags in that fixed source. Current and source pool orders come from
the pre-repair `card_pool_reference.json` source/JDK8/17 reconstruction.

There are 312 cases across four role pools and six seeds. Each case records
selected IDs, calls and final XS128 state/counter for card, card_random, neow
and misc streams. Seed 42 cases remove the first current common card while
retaining source pools. Seed -1 cases start with rarity offset -40.

288 cases execute original JAR methods. They cover Discovery's two private
generators, ForeignInfluenceAction's private generator, NeowReward's colored
and colorless generators with both rare flags, and the three underlying
transform helpers. The player, metadata cards and render initialization are
explicitly prepared inputs. Card effects, normal room acquisition and a full
original game session are outside this component reference.

24 Library cases execute a source-reconstructed acceptance/retry/grid-order
loop calling original JAR rollRarity/getCard helpers. They use an empty relic
list. They do not execute the original event UI or preview callbacks.
Python integration regressions separately exercise preview timing, the real
card-play action, menus, transformation actions and obtain callbacks.

For reproduction, compile both Java drivers with JDK17 and the original JAR
on the classpath. Run SpecialCardReference in a temporary working directory,
passing absolute paths for card_pool_reference.json, special_card_catalog.json
and the output JSON. Static JAR initialization writes display/log bookkeeping
in its working directory. `original_reward_reference.md` describes the shared
headless preparation in more detail.

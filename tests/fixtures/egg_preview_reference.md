# Egg preview component reference

Fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
EggPreviewReference.java executes the actual original MoltenEgg2, ToxicEgg2 and
FrozenEgg2 onPreviewObtainCard/onObtainCard methods. Headless initialization
reuses RewardReference.java.

The deterministic gzip contains 672 rows across all eight egg combinations,
seven original card IDs/types, starting upgrade levels 0/1/2, availability
flags and single/multiple-upgrade limits. Each row applies two previews, an
obtain callback and another preview, recording the four resulting levels.
Original card and merchant RNG state/counters are recorded after the sequence.
The cards use original catalog metadata with explicitly prepared upgradeability.
Their upgrade method changes the upgrade flag and count. This exercises the
original egg guards over prepared inputs. Python numeric effect regressions
use the actual project card implementations.

Python preview tests run the shared production preview helper and actual
AddCardAction, comparing every level and both random states. Status/curse
cards, already upgraded multi-upgrade cards and Flame Barrier's original SKILL
metadata are represented. Availability/upgrade limits are explicit case inputs.

The project integration suite covers 192 normal full inventories across four
roles, A0/A20, all egg combinations and three seeds. Observers forward actual
preview processing and compare all gameplay RNG states before/after each call.
Forty-eight prepared store inventories execute real egg purchase and subsequent
colored/colorless purchases. Ninety-six Courier cases each perform two actual
purchases and observe preview before replacement pricing. Numeric regressions
check damage, block, cost, names and purchase identity, including Searing Blow.
Extension-type fallback, sold-card exclusion and initial price/preview/sale
ordering have dedicated regressions.

The three shop callback locations follow the fixed ShopScreen.initCards,
purchaseCard and StoreRelic.purchaseRelic source call sites. Native project
entry points execute in the integration suite. Complete original game acceptance
remains pending.

Compile RewardReference.java and EggPreviewReference.java with JDK17 and the
fixed JAR on the classpath. Run EggPreviewReference with absolute paths for
special_card_catalog.json and an output JSON file. Use a temporary working
directory for JAR bookkeeping. Gzip uses mtime zero. Raw output and fixed-source
fingerprints are retained in the local repair evidence.

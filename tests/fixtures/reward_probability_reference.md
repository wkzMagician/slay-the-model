# Reward probability component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
RewardProbabilityReference.java executes original AbstractRoom.addPotionToRewards
and AbstractChest.open methods. It reuses RewardReference.java and
ContentPoolReference.java for headless setup, potion localization and helpers.

The deterministic gzip contains 917 rows. There are 896 potion rows across
four roles, ordinary/elite rooms, White Beast Statue held/unheld, prepared
effective chances -10/0/10/40/90/100/110, seeds 0/1/42/20261115 and sequences
of one/eight battles. Each original room has a defeated nonescaped metadata
monster. Reward lists are cleared before each call, explicitly preparing
eligibility below the original four-reward cap. Negative initial chances
without the statue are prepared boundary inputs. The statue's continuing
negative hidden modifier is naturally reachable through repeated drops.

Original drop selection, unbounded blizzardPotionMod update, weighted rarity,
potion-key selection and actual potion constructors execute. Every stage
records the generated canonical potion ID or null and effective hidden chance.
Every integer call and final potion RNG state/counter is retained. Python
executes actual CombatRoom._handle_victory and the selected AddRandomPotionAction,
with ample prepared inventory capacity for sequence comparisons. This component
does not execute original combat or original reward UI/receipt. Full inventory
is verified separately with the native project receipt menu.

Eighteen seeded gold rows cover base amounts 25/50/75 and seeds
0/1/42/-1/999/20261115. AbstractChest.open executes with goldReward=true and
explicit relic tier. RecordingRoom captures addGoldToRewards and ignores the
unrelated relic receipt. Audio and reward-screen opening are recording/no-op
boundaries. The original float32 bound multiplication, actual treasure RNG
float draw and Math.round execute. Calls and final state are compared with
the production conditional gold helper. Gson float values are reprojected to
float32 when comparing their exact binary values in Python.

Three gold-grid rows each supply 1017 explicit nextFloat inputs, including
1000 uniform midpoints, zero, maximum sub-one float32 and neighboring values
around five rounding boundaries. An original RandomXS128 subclass returns each
prepared nextFloat while AbstractChest.open and the original float arithmetic
still execute. Python forwards its real helper using the same prepared raw
float. The medium midpoint grid yields endpoints 45/55 fifty times each and
integers 46 through 54 one hundred times each. Grid raw RNG state is outside
this explicitly controlled-input comparison.

Native project tests execute 192 actual lethal card plays followed by the
reward composer and actual potion generation/receipt across four roles,
A0/A20, normal/elite, statue held/unheld, three chance boundaries and full/open
inventory. They compare the corresponding original potion vector and handle
the full-bar skip choice through the normal input resolver. Another 144 actual
OpenChestAction entries use explicit gold/tier gates and genuine float amount
draws, checking idempotence and isolated gold receipt with Ectoplasm/Bloody Idol.
Three no-gold controls ensure conditional amount sampling is skipped.

The complete gold/tier joint protocol remains EVT-008. Reward eligibility,
independent reward acceptance, other gold modifiers and normal full lifecycle
retain their own issue/acceptance scopes. These component results provide
prepared original executions. Complete original-game comparisons remain pending.

To reproduce, decompress the fixture and pass those rows as input JSON.
Compile RewardReference.java, ContentPoolReference.java and
RewardProbabilityReference.java with JDK17 and the fixed JAR on the classpath.
Run RewardProbabilityReference with input/output JSON paths in a temporary
working directory. Gzip uses mtime zero. Local repair evidence retains raw
inputs/output, Java logs, source hashes and regression/type outputs.

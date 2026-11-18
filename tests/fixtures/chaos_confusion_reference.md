# Chaos and Confusion component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
ChaosConfusionReference.java executes the original ConfusionPower.onCardDraw,
AbstractOrb.getRandomOrb(true) and RandomizeHandCostAction.update methods.
Headless setup reuses RewardReference.java, mock localization and metadata
cards with explicit cost, costForTurn and freeToPlayOnce fields.

The deterministic gzip contains 744 rows across seeds 0/1/2/5/42/20261113.
There are 672 Confusion rows, covering base costs -2/-1/0/1/2/3/4, turn
overrides null/0/1/3, both once-free flags, and one/two successive callbacks.
Each callback's final base/turn costs and free flag are recorded. The original
negative-cost guard and same-cost branch execute directly. Python compares
every stage synchronously, integer arguments/results and final RNG state.

Twenty-four orb-helper rows request 1/2/4/10 orbs. Original orb constructors
and the helper execute, recording chosen class names and cardRandomRng.
Localization, textures and display state are prepared. Visual MathUtils
randomness is outside the gameplay stream comparison. Python executes actual
Chaos.on_play and inspects generated AddOrbAction instances before channeling.

Forty-eight combined rows prepare two existing positive-cost cards and
0/1/5/8 newly drawn positive-cost cards, apply original Confusion callbacks
in draw order, then execute original RandomizeHandCostAction.update. They
cover an existing once-free flag and once-free drawn cards. The explicit
callback sequence is based on the fixed player/potion source call sites.
Original DrawCardAction and the potion-use lifecycle are outside this prepared
component. The project suite separately executes real UsePotionAction,
DrawCardsAction and draw-message dispatch.

Combined comparison checks each Confusion stage, effective current payment,
draw-before-oil random allocation and final state. The existing potion's
randint(0,3) and original random(3) traces are normalized to the same closed
range for this portion. Base-cost persistence, turn-field behavior and
negative-card qualification of the potion remain POT-002/POT-003 acceptance
scopes. Original base/turn fields remain present in the raw fixture.

The native suite covers four real character factories, A0/A20, ordinary and
upgraded Chaos, one/three full slots, generation history and overflow effects.
Actual Setup/Forethought play precedes a Confusion draw and actual subsequent
payment/turn reset. Potion entry tests cover Sacred Bark, hand capacity,
No Draw, insufficient cards and discard reshuffling. Other regressions cover
draw-listener visibility, X/unplayable guards and the potion's once-free flag.
Observers delegate production methods. All eleven other gameplay streams are
compared in the component suite. Full original-game acceptance remains pending.

To reproduce, decompress the fixture JSON and pass the rows as input.
Compile RewardReference.java and ChaosConfusionReference.java with JDK17
and the fixed JAR on the classpath. Run ChaosConfusionReference with input
and output JSON paths in a temporary working directory. Result fields are
regenerated from the explicit inputs. Gzip uses mtime zero. Local repair
evidence retains raw input/output, Java logs, old-HEAD failures and hashes.

# Upgrade relic component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
UpgradeShuffleReference.java executes the actual WarPaint.onEquip and
Whetstone.onEquip methods. It reuses RewardReference.java for headless
initialization and supplies a prepared master deck in explicit input order.

The deterministic gzip contains 144 rows across both relics, seeds
0, 1, 42, 999, -1 and 20261112, and twelve decks per relic. Decks cover empty,
no eligible cards, one/two/three/ten candidates, duplicate IDs, mixed types
and colors, unavailable cards, already upgraded cards, multi-upgrade limits
and bottle flags. Each prepared card supplies its type, color, level,
upgrade limit, availability and bottle flag. Its upgrade updates level/name
and records its original slot. Its makeCopy returns a separate untracked
metadata object, allowing the original makeStatEquivalentCopy and effect
constructors to run. Rendering and effect updates are outside this reference.

The original relic performs candidate collection, miscRng.randomLong,
java.util.Collections.shuffle, upgrade selection and bottle checks.
The prepared original player holds no bottle relics. Bottle flags therefore
exercise the guard while description-refresh side effects remain outside
the component scope. The project integration tests prepare a held bottle
binding, acquire the upgrade relic, and start combat to verify that the same
master-card binding produces an upgraded combat copy. Native bottle-selection
menus remain a separate acceptance scope.

Every original row records upgrade order by distinct slot, final levels,
bottle flags, actual parent RNG calls and final state/counter. Python runs
the native AddRelicAction and shared production upgrade actions against the
same metadata, comparing all recorded gameplay fields and the other eleven
gameplay random domains. Actual numeric card effects are verified separately
through real relic acquisition with actual character factories and cards.

The native suite covers four roles, A0/A20, both relics, candidate counts
0/1/2/3/10 and three seeds. It checks object identity/order, real damage/block,
upgraded names, cross-color cards, Searing Blow, bottle binding/combat copies,
explicit namespace/count boundaries and the shared action's sample default.
Normal acquisition through a full run and complete original-game comparisons
remain pending.

To reproduce, decompress the fixture JSON and use its rows as prepared input.
The Java reader consumes relic, seed and deck and regenerates result fields.
Compile RewardReference.java and UpgradeShuffleReference.java with JDK17
and the fixed JAR on the classpath. Run UpgradeShuffleReference with input
JSON and output JSON paths. Use a temporary working directory for JAR
bookkeeping. Gzip uses mtime zero. Local repair evidence retains original
inputs/output, Java logs and fixed-source fingerprints.

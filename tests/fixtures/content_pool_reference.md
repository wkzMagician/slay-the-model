Fixed original Slay the Spire V2.3.4 desktop-1.0.jar has SHA-256
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

`content_pool_reference.json.gz` holds 1176 original-JAR component cases.
The driver is `tests/reference/ContentPoolReference.java`, with headless
initialization reused from RewardReference.java.

24 cases invoke original initializeRelicList/populateRelicPool and Java
shuffle across four roles and six seeds. The relic maps contain explicitly
prepared metadata relics populated from the pre-repair fixed-source catalog.
The driver executes original pool-building code against these maps.

960 cases execute original returnRandomRelicKey/returnEndRandomRelicKey.
Each performs three draws, preserving before/after pools. Cases cover every
tier, both ends, a prepared rejected candidate, an empty requested tier and
all pools empty. Relic canSpawn is a prepared predicate for the specified
blocked IDs. It does not execute the real relic-specific spawn conditions.

192 cases execute original PotionHelper and AbstractDungeon potion selection
methods and real potion constructors. Each performs five draws for uniform,
weighted, each specific rarity and each limited rarity. Potion text and
keyword dictionaries are placeholders and the prepared player has no relics.
Potion effects and natural game acquisition are outside these component cases.

Every case preserves original RNG parameters/results and final XS128 state
and counter. Raw original output is retained in the local repair evidence.
The gzip fixture uses mtime zero for stable bytes.

Compile RewardReference.java and ContentPoolReference.java with JDK17 and the
fixed JAR on the classpath. Run ContentPoolReference with absolute paths to
relic_catalog_reference.json and an output JSON, in a temporary working
directory to contain the JAR's display/log bookkeeping.

The older relic_pool_reference.json is the pre-repair fixed-source/JDK8/17
string-map reconstruction. The older potion_pool_reference.jsonl contains
actual original PotionHelper.getPotions queries. They independently verify
the production catalogs and pool order in Python regressions.

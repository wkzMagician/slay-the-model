# Combat choice component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
CombatChoiceReference.java executes actual MadnessAction.update and
DiscoveryAction.update methods with headless initialization from
RewardReference.java and prepared pools from SpecialCardReference.java.

The deterministic gzip contains 180 rows. Madness has 22 prepared hands
across seeds 0, 1, 42, 999, -1 and 20261112, giving 132 rows. Card metadata
supplies cost, costForTurn and freeToPlayOnce. Input group order is retained.
Empty and ineligible hands, single targets, repeated rejection, ten-card
hands, temporary zero/one/negative costs, free-once flags and prepared
X/unplayable cards with positive turn costs are represented. Every final
cost and free flag, selected index, integer call and RNG state is compared.
The Python turn-cost projection uses base cost when its turn override is
None. Its effective payment getter also incorporates free-once and X energy,
so the production eligibility test reads the turn-cost fields directly.

Discovery has four colors, default/ATTACK/SKILL/POWER variants and seeds
0, 42 and 20261112, giving 48 rows. Original card selectors execute with
prepared catalog cards and pools. A RecordingScreen overrides only
customCombatOpen to capture generated candidates and skippable. Default
Discovery is mandatory. Typed generic variants allow skipping. Candidate
IDs, selection flags, integer calls and final RNG state are compared.
The screen is allocated with Unsafe. Gdx.graphics delegates to the existing
headless proxy and supplies deltaTime 0.01 for action duration processing.

Project integration tests use prepared combat arenas with actual character
factories, four roles, A0/A20, ordinary/upgraded cards and PlayCardAction.
They exercise Bullet Time and Enlightenment before Madness, subsequent
payment and turn reset, mandatory selection retry, manual input parsing and
hand-capacity overflow. RNG observers delegate actual production methods.
The project-specific positive once-cost override has a separate regression.
Discovery's cost and upgraded exhaust defects remain tracked as CARD-007
and CARD-008. Complete games and normal lifecycle acceptance remain pending.

To reproduce, compile RewardReference.java, SpecialCardReference.java and
CombatChoiceReference.java with JDK17 and the fixed JAR on the classpath.
Run CombatChoiceReference with four arguments, the prepared Madness input
JSON, card_pool_reference.json, special_card_catalog.json and output JSON.
Use a temporary working directory for JAR bookkeeping. Local repair
evidence retains reference-inputs.json, raw outputs, source fingerprints
and compiler/runtime logs. The gzip mtime is zero.

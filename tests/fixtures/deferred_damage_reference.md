# Deferred random damage component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
DeferredDamageReference.java executes the actual original update methods of
DamageRandomEnemyAction, LightningOrbPassiveAction and LightningOrbEvokeAction.
It uses original MonsterGroup target selection, cardRandomRng and lock-on
helpers, with a prepared GameActionManager queue and master combat state.

The deterministic gzip contains 240 rows. There are 48 Juggernaut-action,
96 lightning-passive-action and 96 lightning-evoke-action rows. Twelve
prepared enemy configurations and seeds 0/1/42/20261113 cover empty and single
targets, healthy repeated hits, repeated lethal hits, a preceding queued
kill, three hits, lock-on, block, half-dead/escaping/all-dying enemies and
zero damage. Lightning covers both single-target and all-enemy variants.
Input damage is explicit, including already-applied Focus. Source power/orb
callbacks and original Focus application are outside this component scope.

The original target actions enqueue actual DamageAction or
DamageAllEnemiesAction objects. A Java boundary adapter records target/amount
or matrix entries, advances explicitly prepared HP/block and marks zero-HP
targets dying. It skips render, audio and animation actions. It also skips
ineffective targets at the recording boundary. Original monster damage,
death reactions and combat cleanup are outside this adapter's scope.
The fixture records effective damage parameters, final prepared HP/block,
integer calls and final RNG state/counter. The original all-enemy matrix
and single-target lock-on calculations execute in the actual target actions.

Headless preparation reuses RewardReference.java, supplies a dummy VFX atlas
region and Unsafe-allocated metadata monsters/powers. No original gameplay
session is executed. Both Java and Python use explicit half-dead, dying and
escaping flags. Python uses actual project damage/defense/death processing,
and an observer delegates DealDamageAction.execute while recording inputs.
Other eleven gameplay random domains are checked for unchanged state.

The native project suite uses actual character factories, prepared combat
arenas and real card/turn-end entry points. It covers Juggernaut followed by
Iron Wave, Dualcast, Multi-Cast, full-slot channeling, multiple end-turn
lightning orbs, Focus/Electro snapshots and execution-time Lock-On. Separate
regressions cover matrix completion before queued reactions, zero/multiple
Block gains and live Buffer/Intangible/Thorns defenses. Existing cleanup,
other orb and death-message suites are included in targeted/full runs.

To reproduce, decompress the fixture and pass those rows as input JSON.
Compile RewardReference.java and DeferredDamageReference.java using JDK17
and the fixed JAR on the classpath. Run DeferredDamageReference with input
and output JSON paths in a temporary working directory. The reader consumes
the prepared inputs and regenerates output fields. Gzip uses mtime zero.
Local repair evidence retains raw inputs/output, Java logs, source hashes,
old-HEAD failures and final test/type logs. Complete original-game comparison
and normal full lifecycle acceptance remain pending.

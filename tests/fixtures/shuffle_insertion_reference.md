# Shuffle and insertion component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
ShuffleInsertionReference.java executes original CardGroup.addToRandomSpot,
EmptyDeckShuffleAction, ShuffleAllAction, PutOnDeckAction and ShuffleAction.
It reuses RewardReference.java for headless setup and supplies metadata cards,
player piles, a GameActionManager queue and a recording relic callback.

The deterministic gzip has 504 rows across seeds 0/1/2/5/42/20261113.
Seventy-two insertion rows cover pile sizes 0/1/4/10 and one/two/three inserts,
recording every resulting order. Empty insertion consumes zero random values.
Nonempty insertion uses the original inclusive upper bound size minus one.
Python executes actual AddCardAction and compares order, calls and states.
Its randint(0,N-1) trace is normalized to the equivalent JAR random(N-1).

There are 216 Deep Breath and 216 Reboot preparation rows, covering draw sizes
0/1/4, discard sizes 0/1/4 and remaining hand sizes 0/1/3/10. Original action
constructors execute the recording relic's onShuffle. That callback records
both RNG counters before the first shuffle. Original actions perform discard
pre-shuffle, random hand selection/real CardGroup.moveToDeck, and final shuffle.
The Java scheduler completes each current action before taking the next queued
action. Delta time is explicitly 0.01 for the timed hand-return action.

RecordingSouls overrides the animation transfer boundary. Its shuffle and
onToDeck methods perform original immediate drawPile.addToTop and record the
card ID. The original actions/card groups perform source removal and target
selection. Rendering, soul animations, card damage/effects and actual relic
effects are outside this component. Card glow lists, card queue, selection
screen flags, room and the shuffle tutorial flag are explicitly prepared.

Every row retains stage orders, individual transfers, final piles, notification
counters, both random call sequences and final states/counters. Python forwards
actual production shuffle/move methods and verifies pre/final shuffle inputs,
transfer identity/order, notification timing and ten other gameplay streams.
Drawing after preparation is tested through the real project card entry points.
Original DrawCardAction is outside this prepared action component.

The native suite has 128 actual Deep Breath/Reboot plays across four character
factories, A0/A20, ordinary/upgraded cards and four pile scenarios. It checks
drawn object order, both RNG states, actual Abacus block, Sundial energy/count,
and the source card's discard/exhaust cleanup. Forty-eight native combat starts
check Mark of Pain's two Wounds. Ten other regressions cover No Draw, full hand,
ordinary nonempty-discard refill and relic effects before preparation.

DrawAfterShuffleAction limits these two cards' draw requests to currently
available cards before delegating DrawCardsAction. Ordinary double-empty draw
refill remains tracked under CARD-019. Tantrum's separate source-card cleanup
issue remains CARD-086. Full original-game and normal lifecycle acceptance
remain pending.

To reproduce, decompress the fixture JSON and pass its rows as input.
Compile RewardReference.java and ShuffleInsertionReference.java with JDK17 and
the fixed JAR on the classpath. Run ShuffleInsertionReference with input/output
JSON paths in a temporary working directory. Gzip uses mtime zero. Local repair
evidence retains raw inputs/output, Java logs, source hashes and test results.

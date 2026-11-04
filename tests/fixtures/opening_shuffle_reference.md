# Opening shuffle reference

Generated on 2026-11-03 with the fixed original `desktop-1.0.jar` Random class
and JDK 17.0.11 `Collections.shuffle`. JAR SHA-256:
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

15 cases: internal seeds 0, 1, 523, 524, -1; deck sizes 0, 1, 12.
Each case creates a fresh original Random, consumes `randomLong()` for a Java48
child seed, and shuffles integer card labels using that child seed. It then
reproduces the fixed `CardGroup.initializeDeck` stable partition: labels divisible
by 3 are innate, labels divisible by 5 are bottled; either property places a card
on top, with overlap counted once. `next_card_first` reverses the resulting
bottom-to-top group. `next_parent_long` checks the parent's continuation.

The shuffle and RNG are actual JAR/JDK execution; the labeled-card partition is
source-derived. This does not execute original CardGroup or a gameplay session.
Original source: `com/megacrit/cardcrawl/cards/CardGroup.java`, `shuffle(Random)`
and `initializeDeck(CardGroup)`, V2.3.4 / 2022-12-18 / CFR 0.152.

The local audit directory `.bugs/fixes/p3-opening-draw-2026-11-03` preserves the
Java generator, commands, validation, and source fingerprints. The fixture is
independent of the Python implementation and must not be regenerated from it.

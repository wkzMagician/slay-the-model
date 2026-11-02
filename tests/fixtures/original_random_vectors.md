Original-game utility reference, recorded 2026-10-29. This is not a game-session
recording. No game JAR is distributed here.

`original_random_vectors.jsonl.gz` contains 5444 unchanged JSONL records, compressed
with gzip. Uncompressed SHA-256:
`5588bf214b82fadd045d7c540dc5ea5548bab2bae86c81291c1d6bc55991608c`.

Source: fixed Slay the Spire V2.3.4 / 2022-12-18 desktop JAR, SHA-256
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
The original Random, RandomXS128 and SeedHelper classes and JDK utility methods
produced identical records in two JDK17 runs and one JDK8 run. Local detailed
provenance and oracle sources: `.bugs/checks/random-reference-2026-10-29/`.

Categories include utility API fixtures with manufactured states, synthetic
ordered lists for shuffle, and source-shaped float/round examples. These do not
prove map, content consumer, save-game, or complete run parity.

The production copy API accepts an explicit MathUtils RNG to reproduce the
original copy constructor's discarded draws, without creating a hidden global
random source. Tests provide the recorded controlled MathUtils state.

# Gold source reference

Fixed V2.3.4 desktop-1.0.jar SHA-256 cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673.

GoldOriginReference.java executes actual RewardItem constructors and AbstractPlayer.gainGold for 360 prepared inputs. Inputs cover direct income, combat rewards, event combat rewards, ordinary treasure room rewards and stolen rewards, 18 amounts including zero/negative controls, Golden Idol and Ectoplasm combinations. The original Ironclad object and room/relic metadata are prepared with Unsafe using the existing reference setup. Observer relic callbacks record gold after the original receipt. Relic flash and callback bodies are observation boundaries. Original Bloody Idol healing and reward claiming UI are outside this component reference.

The 44 boss arithmetic rows use the source-derived AbstractRoom ascension branch and actual JAR MathUtils.round for every base 95 through 105 and A0/A12/A13/A20. They do not execute original boss combat or AbstractRoom victory handling. Python tests separately execute prepared lethal card plays followed by the production reward composer.

Compile RewardReference.java, ContentPoolReference.java, RewardProbabilityReference.java and GoldOriginReference.java against the fixed JAR with JDK17, then run GoldOriginReference with a JSON output path. Compress output as gold_origin_reference.json.gz with gzip mtime=0. The fixture contains no wall-clock data.

Local evidence and command logs are in .bugs/fixes/p4-gold-origins-2026-11-15. Run tests/test_gold_origin_protocols.py through the repository test wrapper. Full original gameplay and same-seed full-run comparisons remain pending.

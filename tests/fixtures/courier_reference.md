# Courier restock component reference

Fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
CourierReference.java reconstructs the small restock loops from ShopScreen and
StoreRelic. It calls actual original selection, canSpawn and pricing methods.
The normal dungeon colorless threshold is explicitly prepared as 0.3f, matching
Exordium, TheCity, TheBeyond and TheEnding. Whole purchase UI, callbacks and
original game sessions are outside the Java driver.

The deterministic gzip contains 204 rows.

- 192 colorless rows cover four roles, A0/A20, Membership presence, two sold
  rarities and six seeds. Each performs three replacements using original
  merchantRng.random, getColorlessCardFromPool and private ShopScreen.setPrice.
  Card metadata/pools and Courier ownership are explicit inputs. A metadata
  copy preserves original color/type for pricing. IDs, new tiers, prices,
  merchant/card calls and both final XS128 states/counters are retained.
- 12 relic rows prepare ordered pools, room type, floor and explicit tier
  schedules. Actual returnRandomRelicEnd and real relic-specific canSpawn
  implementations execute. Non-gated relic entries use metadata doubles.
  The source-reconstructed outer loop rejects the four original classes after
  a candidate has been drawn. It covers consecutive rejects outside a ShopRoom,
  qualification rejects inside a ShopRoom, floor cutoffs, tier exhaustion and
  Circlet fallback. Courier/Membership ownership is prepared after selection
  for the actual getNewPrice invocation. These rows isolate the component
  without claiming a natural acquisition/pool history for the prepared inputs.

Python uses production restock_shop_item and normal selectors. Relic rows fix
only the outer tier sequence and compare attempts, remaining pools, final item,
price and merchant calls/state. SHOP-014 independently owns tier probabilities
and their RNG protocol, so these prepared schedules provide no acceptance of
that issue. Unit regressions additionally forward real ordered-pool selection
for shop qualification and check one tier roll per outer rejection.

Compile RewardReference.java, ContentPoolReference.java, SpecialCardReference.java,
RelicSpawnReference.java and CourierReference.java with JDK17 and the fixed JAR.
Run CourierReference with paths to relic_catalog_reference.json,
card_pool_reference.json, special_card_catalog.json, relic-input JSON and output
JSON. The relic rows in the fixture are replay inputs, with output fields
ignored/overwritten. Use a temporary working directory for display/log files.
Gzip uses mtime zero. Raw output, explicit schedules and source fingerprints
are retained in local repair evidence.

Native Python integration covers 24 prepared shop-tier relic purchases with
second purchases, and 96 prepared colorless-slot two-purchase runs across all
roles, A0/A20, three seeds, sold rarities and Membership presence. Courier uses
the actual obtain action/history. Relic tests explicitly fix the outer rarity
to isolate SHOP-008 from SHOP-014. Boundary regressions cover strict float32
0.3 comparisons, all four rejected classes, no-price-on-reject and absent
provider results. Previews/upgrades and complete same-seed runs remain separate.

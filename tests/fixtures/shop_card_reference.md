# Shop card component reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
ShopCardReference.java reconstructs Merchant's five-slot acceptance loop from
that source. Each attempt calls the actual JAR rollRarity/getCardFromPool
methods. Two subsequent draws call the actual getColorlessCardFromPool.
The Merchant UI constructor and ShopScreen pricing are outside this driver.

Headless initialization and metadata cards/pools reuse RewardReference.java
and SpecialCardReference.java. Card pool order comes from the independent
card_pool_reference.json and metadata from special_card_catalog.json.
The driver runs four roles, A0/A20, offsets 5/-40 and seeds 0 through 31.
It records 512 original-helper cases, including the explicit attempted slot,
rarity and selected ID, RNG parameters/results and final state/counter.

The committed deterministic gzip contains the 308 cases whose power slot does
not require the separately pending SHOP-004 rarity fallback. These include
42 cases with duplicate rejection. Python calls production shop generators
and compares all seven IDs, all card RNG calls, rarity offset and final state.
The other 204 cases and all original output remain in local repair evidence.
Selection depends on the original attempted power rarity, before comparing
Python output. There is no assertion of complete shop parity. SHOP-010 price
distribution and SHOP-004 fallback have separate repair scopes.

Compile RewardReference.java, SpecialCardReference.java and ShopCardReference.java
with JDK17 and the fixed JAR on the classpath. Run ShopCardReference with absolute
paths for card_pool_reference.json, special_card_catalog.json and an output JSON.
Use a temporary directory to contain original log/display bookkeeping. Filter
rows where power_fallback is false to reproduce the gzip with mtime zero.

Shop phase-order tests use explicit injected card/item providers and trace
price calls. Native ShopRoom.init regressions separately cover four roles,
A0/A20 and four seeds with real production generators and forwarding RNG
observers. These tests establish phase/stream routing. Exact original prices,
whole original UI execution and complete normal runs have separate acceptance.

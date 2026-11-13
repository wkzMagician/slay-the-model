# Merchant card-pool and tier protocol reference

The fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
MerchantProtocolReference.java produces 376 prepared component rows.

- 100 grid rows execute actual ShopScreen.rollRelicTier with scripted original
  integer outcomes 0 through 99. They record the original random(99) argument
  and resulting tier. Counts are COMMON48, UNCOMMON34, RARE18.
- 192 card rows follow the fixed Merchant acceptance loop and execute actual
  original rollRarity/getCardFromPool/getColorlessCardFromPool. Inputs cover
  four role pools, A0/A20, Prismatic Shard presence, two rarity offsets and six
  seeds. Card IDs, all calls, rarity offset and final card state are retained.
  Metadata cards and held relics are prepared explicitly.
- 12 initial rows execute actual private ShopScreen.initRelics with prepared
  ordered pools, an empty master deck and ShopRoom context, at A0/A20 and six
  seeds. Both random tier rolls, all three base-price rolls, the SHOP slot,
  remaining pools, selected IDs/prices and final merchant state are recorded.
- 72 restock rows follow StoreRelic's acceptance loop with actual
  ShopScreen.rollRelicTier, returnRandomRelicEnd and getNewPrice. They cover
  ShopRoom/other room contexts, floor cutoffs, exhaustion/Circlet and Membership
  presence. Twelve rows reject candidates and take more than one attempt,
  with a maximum of five attempts. Tier draws consume the actual original RNG.

Headless initialization reuses RewardReference and ContentPoolReference.
RelicSpawnReference supplies actual gated original relic classes. Other relics
and cards use metadata objects. Localization, textures and inventory wrappers
are explicit preparation. Restock selection starts with an empty owned list,
then Courier/Membership are prepared for getNewPrice. These inputs isolate the
consumer and record the ownership timing used in the component.

Python executes real production selectors, tier rolls and restock processing.
Initial rows call generate_shop_items with an empty card-candidate provider so
merchantRng starts at the initRelics boundary. A forwarding potion provider
captures calls/state immediately after relic generation. Prices of the later
potion phase continue through production. The comparison checks the recorded
relic-phase boundary, raw item prices and remaining relic pools.

Native regressions additionally cover 64 full shop initializations and three
purchases each, four roles, A0/A20, Shard presence and four seeds. They check
role scope, both initial ordinary-tier integer calls, slot counts, menu prices,
payment and replacement availability. Eight combat-reward tests forward the
real reward generator and check Shard's all-color reward scope.

Compile RewardReference.java, ContentPoolReference.java, SpecialCardReference.java,
RelicSpawnReference.java and MerchantProtocolReference.java with JDK17 and the
fixed JAR on the classpath. Run MerchantProtocolReference with five arguments,
relic_catalog_reference.json, card_pool_reference.json, special_card_catalog.json,
a JSON array of initial/restock inputs and an output JSON path. Extract initial
and restock rows from the fixture to replay those inputs. Output fields are
replaced by the driver. Use a temporary working directory for JAR bookkeeping.
The gzip uses mtime zero. Raw output and source fingerprints are in the local
repair evidence. Full-game acceptance remains pending.

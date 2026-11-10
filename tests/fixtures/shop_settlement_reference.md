# Shop settlement component reference

Fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.
ShopSettlementReference.java reuses RewardReference's headless initialization,
ContentPoolReference's metadata relics, and ShopPriceReference's float RNG trace.
Cards, inventory wrappers, relic ownership and hidden removal base are prepared
inputs. Textures/text are placeholders. Whole original shop UI and gameplay
are outside this reference.

The deterministic gzip contains 648 rows.

- 512 initial/dynamic rows execute actual ShopScreen.applyDiscount over prepared
  card, relic and potion inventories. Eight base prices, four ascensions,
  sale presence and all Courier/Membership/Smiling Mask combinations are covered.
  The source-defined initial call order is reconstructed. Sale division is
  prepared before those calls. A subsequent actual applyDiscount(0.5,true)
  records dynamic prices and the overwrite of the removal quote from purgeCost.
  Duplicate Membership flags in these component rows are explicit repeated
  multiplier inputs. Native acquisition tests cover purchase while unowned.
- 40 removal rows execute actual applyDiscount calls for initial service quotes
  over five hidden bases and all three-relic combinations. The post-removal
  quote is source-reconstructed from purgeCard's numeric branch and uses actual
  MathUtils.round. Here base is the already-updated hidden base. purgeCard,
  payment, card selection and hidden-base increment are outside this oracle.
- 96 relic/potion restock rows execute actual ShopScreen.getNewPrice overloads
  over six prepared bases, both discount flags and four seeds. Both resulting
  prices, float RNG calls and final XS128 state/counter are retained.

Python compares real ShopRoom quote preparation, purchase-discount handling,
service helpers and ShopItem restock settlement to these results. The original
getNewPrice method receives the unvaried base. Python prepares its rounded
randomized base with the source-defined formula and then exercises production
restock settlement. Separate integration tests cover complete production restock.
The existing 100 actual original card setPrice rows remain active unchanged.

Compile RewardReference.java, ContentPoolReference.java, ShopPriceReference.java
and ShopSettlementReference.java with JDK17 and the fixed JAR on the classpath.
Run ShopSettlementReference with one output-JSON path in a temporary directory.
Gzip uses mtime zero. Raw output and source fingerprints remain in local batch
repair evidence. The source call ordering and post-removal arithmetic are
explicit reconstruction steps. They do not constitute original game sessions.

Native tests cover 192 prepared-inventory menu/affordability/payment cases,
eight actual Membership purchases, repeated menu refresh, four removal and
cross-visit cases, the sale/rounding boundaries and legacy unquoted items.
The existing deletion-confirmation and masked hidden-base increment issues
SHOP-006/007 remain independent acceptance scopes.

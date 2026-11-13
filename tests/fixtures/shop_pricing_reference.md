# Shop fallback and pricing references

Fixed V2.3.4 desktop-1.0.jar SHA-256 is
`cfad868ac8d65a88e71a0bf096fb09f78811e553effe0787c5309a655e081673`.

`shop_card_fallback_reference.json.gz` contains the 204 power-fallback cases
retained from the previous 512-case ShopCardReference execution. The previous
308-case fixture is preserved. Together they compare all seven candidate IDs,
card RNG calls/state and rarity offset across four roles, A0/A20, two offsets
and 32 seeds. The Merchant acceptance loop is source-reconstructed, while
rollRarity/getCardFromPool/getColorlessCardFromPool execute original JAR methods
against explicitly prepared metadata cards and pools. Reproduction details
remain in shop_card_reference.md. Original constructors/effects are outside
this candidate reference.

`shop_price_reference.json.gz` contains 178 rows from ShopPriceReference.java.
There are 65 seeded initial-price rows, 13 quantile grids and 100 card-restock
rows. Each seeded/restock row has 20 prices. Each grid has 1000 midpoints and
quantiles zero, one half and the greatest float below one. The 13 categories
cover three colored, two colorless, three potion and five relic tiers, including
SHOP and SPECIAL relic exhaustion fallback pricing.

Initial-price rows execute actual original getPrice methods, RNG and
MathUtils.round, with the arithmetic sequence reconstructed from ShopScreen
initCards/initRelics/initPotions. The original initial-stock UI is outside this
driver. Card-restock rows invoke actual private ShopScreen.setPrice with
explicitly prepared cards and Courier/Membership flags. RewardReference's
headless initialization and ContentPoolReference's metadata relics are reused.
Potion text is a placeholder, and an Unsafe-allocated original FirePotion has
its rarity prepared before executing inherited getPrice. Effects are outside
this price reference.

Python seeded rows compare every result, float RNG call and final XS128 state
and counter. Grid rows compare exact float32 arithmetic and prices. Card-restock
rows run production restock_shop_item and ShopItem price retrieval with selected
candidate/outer rarity explicitly fixed, because setPrice receives an already
selected card. A20 is supplied to the Python retrieval to check that this
restock-specific pricing entry preserves the original setPrice behavior.
Original prices apply Courier then Membership before the final int cast.

Compile RewardReference.java, ContentPoolReference.java and ShopPriceReference.java
with JDK17 and the fixed JAR. Run ShopPriceReference with one output-JSON path.
Use a temporary working directory for log/display bookkeeping. Gzip uses mtime
zero. The old 308-case fixture and its historical explanation remain unchanged.

Production integration separately covers 160 real ShopRoom.init cases across
roles, A0/A20, Prismatic Shard presence and ten seeds, plus 16 two-purchase
Courier runs with actual selection and pricing. The purchase tests explicitly
force COMMON for the outer restock rarity to exercise fallback. SHOP-002 still
tracks the existing purchase ascension-field discrepancy, and SHOP-003 tracks
initial inventory/removal discount ordering. Whole-shop and complete normal-run
parity have separate acceptance scopes.

// Source-reconstructed Courier loops calling actual original selectors/pricing.
// Relic tier schedules are explicit inputs because SHOP-014 is a separate scope.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.core.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.relics.*;
import com.megacrit.cardcrawl.rooms.*;
import com.megacrit.cardcrawl.shop.*;
import com.google.gson.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

public class CourierReference {
    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public float random() {
            float value=super.random();calls.add(Arrays.asList("float",(double)value));return value;
        }
        public float random(float low,float high) {
            float value=super.random(low,high);
            calls.add(Arrays.asList("float_range",(double)low,(double)high,(double)value));return value;
        }
    }
    static void owned(boolean membership) throws Exception {
        AbstractDungeon.player.relics.clear();
        AbstractDungeon.player.relics.add(ContentPoolReference.relic("The Courier","UNCOMMON"));
        if (membership) AbstractDungeon.player.relics.add(ContentPoolReference.relic("Membership Card","SHOP"));
    }
    public static void main(String[] args) throws Exception {
        JsonParser parser=new JsonParser();
        JsonObject relicCatalog=parser.parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject();
        ContentPoolReference.setup(relicCatalog.getAsJsonArray("rows"));
        Field strings=LocalizedStrings.class.getDeclaredField("relics");strings.setAccessible(true);
        strings.set(null,new HashMap<String,RelicStrings>() {
            public RelicStrings get(Object id) {
                RelicStrings value=new RelicStrings();value.NAME=id.toString();value.FLAVOR="prepared";
                value.DESCRIPTIONS=new String[100];Arrays.fill(value.DESCRIPTIONS,"prepared");return value;
            }
        });
        for (JsonElement entry:relicCatalog.getAsJsonArray("rows")) {
            JsonObject row=entry.getAsJsonObject();RelicSpawnReference.relics.put(row.get("id").getAsString(),row);
        }
        for (JsonObject row:RelicSpawnReference.relics.values()) {
            if (row.get("can_spawn_source").isJsonNull()) continue;
            String id=row.get("id").getAsString();
            ContentPoolReference.relicMap("sharedRelics").put(id,RelicSpawnReference.actualRelic(id));
        }
        SpecialCardReference.pools=parser.parse(new String(Files.readAllBytes(Paths.get(args[1])),"UTF-8")).getAsJsonObject().getAsJsonArray("pools");
        for (JsonElement entry:parser.parse(new String(Files.readAllBytes(Paths.get(args[2])),"UTF-8")).getAsJsonArray()) {
            JsonObject row=entry.getAsJsonObject();SpecialCardReference.metadata.put(row.get("id").getAsString(),row);
        }
        ShopScreen screen=(ShopScreen)RewardReference.u.allocateInstance(ShopScreen.class);
        Method setPrice=ShopScreen.class.getDeclaredMethod("setPrice",AbstractCard.class);setPrice.setAccessible(true);
        List<Object> output=new ArrayList<>();
        for (String color:new String[]{"RED","GREEN","BLUE","PURPLE"}) {
            for (int asc:new int[]{0,20}) for (boolean membership:new boolean[]{false,true}) for (String oldTier:new String[]{"UNCOMMON","RARE"}) for (long seed:new long[]{0,1,42,999,-1,20261110}) {
                owned(membership);SpecialCardReference.preparePools(color);AbstractDungeon.ascensionLevel=asc;
                AbstractDungeon.colorlessRareChance=0.3f;
                Trace merchant=new Trace(seed);SpecialCardReference.Trace card=new SpecialCardReference.Trace(seed+1);
                AbstractDungeon.merchantRng=merchant;AbstractDungeon.cardRng=card;
                List<Object> replacements=new ArrayList<>();
                for (int i=0;i<3;i++) {
                    AbstractCard.CardRarity tier=merchant.random()<AbstractDungeon.colorlessRareChance?AbstractCard.CardRarity.RARE:AbstractCard.CardRarity.UNCOMMON;
                    AbstractCard candidate=AbstractDungeon.getColorlessCardFromPool(tier);
                    // Prepared metadata copy preserves the original color/type for setPrice.
                    AbstractCard copy=SpecialCardReference.card(candidate.cardID);setPrice.invoke(screen,copy);
                    replacements.add(Arrays.asList(copy.cardID,tier.name(),copy.price));
                }
                Map<String,Object> row=new LinkedHashMap<>();
                row.put("kind","colorless");row.put("color",color);row.put("ascension",asc);row.put("membership",membership);row.put("old_tier",oldTier);row.put("seed",Long.toString(seed));row.put("results",replacements);
                row.put("merchant_calls",merchant.calls);row.put("card_calls",card.calls);row.put("merchant_state",RewardReference.state(merchant));row.put("card_state",RewardReference.state(card));output.add(row);
            }
        }
        JsonArray scenarios=parser.parse(new String(Files.readAllBytes(Paths.get(args[3])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:scenarios) {
            JsonObject row=entry.getAsJsonObject();
            Settings.isEndless=false;AbstractDungeon.floorNum=row.get("floor").getAsInt();AbstractDungeon.actNum=1;
            AbstractDungeon.player.relics.clear();
            MapRoomNode node=new MapRoomNode(0,0);node.setRoom(row.get("shop").getAsBoolean()?new ShopRoom():new MonsterRoom());AbstractDungeon.currMapNode=node;
            for (String tier:ContentPoolReference.TIERS) {
                ContentPoolReference.pool(tier).clear();
                for (JsonElement id:row.getAsJsonObject("before").getAsJsonArray(tier)) ContentPoolReference.pool(tier).add(id.getAsString());
            }
            List<String> attempts=new ArrayList<>();AbstractRelic candidate;
            int count=0;
            do {
                String tier=row.getAsJsonArray("tiers").get(count++).getAsString();
                candidate=AbstractDungeon.returnRandomRelicEnd(AbstractRelic.RelicTier.valueOf(tier));attempts.add(candidate.relicId);
            } while (candidate instanceof OldCoin || candidate instanceof SmilingMask || candidate instanceof MawBank || candidate instanceof Courier);
            owned(row.get("membership").getAsBoolean());
            Trace merchant=new Trace(20261110);AbstractDungeon.merchantRng=merchant;
            StoreRelic wrapper=(StoreRelic)RewardReference.u.allocateInstance(StoreRelic.class);wrapper.price=candidate.getPrice();screen.getNewPrice(wrapper);
            row.addProperty("kind","relic");row.addProperty("result",candidate.relicId);row.addProperty("price",wrapper.price);row.add("attempts",new Gson().toJsonTree(attempts));row.add("after",new Gson().toJsonTree(ContentPoolReference.poolState()));
            row.add("merchant_calls",new Gson().toJsonTree(merchant.calls));row.add("merchant_state",new Gson().toJsonTree(RewardReference.state(merchant)));output.add(row);
        }
        Files.write(Paths.get(args[4]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Courier component rows "+output.size());
    }
}

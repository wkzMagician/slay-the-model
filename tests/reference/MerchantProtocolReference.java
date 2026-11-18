// Actual original merchant tier RNG, relic initialization and selector methods.
// Card and restock acceptance loops follow the fixed source with prepared state.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.core.Settings;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.relics.*;
import com.megacrit.cardcrawl.rooms.*;
import com.megacrit.cardcrawl.shop.*;
import com.google.gson.*;
import java.lang.reflect.*;
import java.nio.file.*;
import java.util.*;

public class MerchantProtocolReference {
    static class Trace extends RewardReference.Trace {
        Integer forced;
        Trace(long seed) { super(seed); }
        public int random(int bound) {
            if (forced != null) {
                calls.add(Arrays.asList("int",bound,forced));
                return forced;
            }
            return super.random(bound);
        }
        public float random(float low,float high) {
            float value=super.random(low,high);
            calls.add(Arrays.asList("float_range",(double)low,(double)high,(double)value));
            return value;
        }
    }
    static void prepare(JsonObject input) throws Exception {
        AbstractDungeon.player.relics.clear();
        AbstractDungeon.player.masterDeck=new CardGroup(CardGroup.CardGroupType.MASTER_DECK);
        AbstractDungeon.floorNum=input.get("floor").getAsInt();
        AbstractDungeon.actNum=AbstractDungeon.floorNum<17?1:3;
        MapRoomNode node=new MapRoomNode(0,0);
        node.setRoom(input.get("shop").getAsBoolean()?new ShopRoom():new MonsterRoom());
        AbstractDungeon.currMapNode=node;
        for (String tier:ContentPoolReference.TIERS) {
            ContentPoolReference.pool(tier).clear();
            for (JsonElement key:input.getAsJsonObject("before").getAsJsonArray(tier)) {
                ContentPoolReference.pool(tier).add(key.getAsString());
            }
        }
    }
    public static void main(String[] args) throws Exception {
        JsonParser parser=new JsonParser();
        JsonObject catalog=parser.parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject();
        ContentPoolReference.setup(catalog.getAsJsonArray("rows"));
        Field strings=LocalizedStrings.class.getDeclaredField("relics");
        strings.setAccessible(true);
        strings.set(null,new HashMap<String,RelicStrings>() {
            public RelicStrings get(Object key) {
                RelicStrings result=new RelicStrings();
                result.NAME=key.toString();result.FLAVOR="prepared";
                result.DESCRIPTIONS=new String[100];Arrays.fill(result.DESCRIPTIONS,"prepared");
                return result;
            }
        });
        for (JsonElement entry:catalog.getAsJsonArray("rows")) {
            JsonObject row=entry.getAsJsonObject();
            RelicSpawnReference.relics.put(row.get("id").getAsString(),row);
        }
        for (JsonObject row:RelicSpawnReference.relics.values()) {
            if (!row.get("can_spawn_source").isJsonNull()) {
                String id=row.get("id").getAsString();
                ContentPoolReference.relicMap("sharedRelics").put(id,RelicSpawnReference.actualRelic(id));
            }
        }
        SpecialCardReference.pools=parser.parse(new String(Files.readAllBytes(Paths.get(args[1])),"UTF-8")).getAsJsonObject().getAsJsonArray("pools");
        for (JsonElement entry:parser.parse(new String(Files.readAllBytes(Paths.get(args[2])),"UTF-8")).getAsJsonArray()) {
            JsonObject row=entry.getAsJsonObject();
            SpecialCardReference.metadata.put(row.get("id").getAsString(),row);
        }
        Settings.isEndless=false;Settings.isDailyRun=false;
        List<Object> output=new ArrayList<>();
        for (int roll=0;roll<100;roll++) {
            Trace rng=new Trace(0);rng.forced=roll;AbstractDungeon.merchantRng=rng;
            Map<String,Object> row=new LinkedHashMap<>();
            row.put("kind","grid");row.put("roll",roll);
            row.put("tier",ShopScreen.rollRelicTier().name());row.put("calls",rng.calls);
            output.add(row);
        }
        long[] seeds={0,1,42,999,-1,20261111};
        for (String color:new String[]{"RED","GREEN","BLUE","PURPLE"}) {
            for (int asc:new int[]{0,20}) for (boolean shard:new boolean[]{false,true}) for (int offset:new int[]{5,-40}) for (long seed:seeds) {
                SpecialCardReference.preparePools(color);
                AbstractDungeon.player.relics.clear();
                if (shard) AbstractDungeon.player.relics.add(ContentPoolReference.relic("PrismaticShard","SHOP"));
                AbstractDungeon.ascensionLevel=asc;AbstractDungeon.cardBlizzRandomizer=offset;
                MapRoomNode node=new MapRoomNode(0,0);node.setRoom(new ShopRoom());AbstractDungeon.currMapNode=node;
                SpecialCardReference.Trace rng=new SpecialCardReference.Trace(seed);AbstractDungeon.cardRng=rng;
                List<String> cards=new ArrayList<>();
                AbstractCard.CardType[] types={AbstractCard.CardType.ATTACK,AbstractCard.CardType.ATTACK,AbstractCard.CardType.SKILL,AbstractCard.CardType.SKILL,AbstractCard.CardType.POWER};
                for (int index=0;index<types.length;index++) {
                    AbstractCard candidate;
                    do {
                        candidate=AbstractDungeon.getCardFromPool(AbstractDungeon.rollRarity(),types[index],true);
                    } while (candidate.color==AbstractCard.CardColor.COLORLESS || ((index==1 || index==3) && candidate.cardID.equals(cards.get(index-1))));
                    cards.add(candidate.cardID);
                }
                cards.add(AbstractDungeon.getColorlessCardFromPool(AbstractCard.CardRarity.UNCOMMON).cardID);
                cards.add(AbstractDungeon.getColorlessCardFromPool(AbstractCard.CardRarity.RARE).cardID);
                Map<String,Object> row=new LinkedHashMap<>();
                row.put("kind","cards");row.put("color",color);row.put("ascension",asc);
                row.put("shard",shard);row.put("offset",offset);row.put("seed",Long.toString(seed));
                row.put("cards",cards);row.put("calls",rng.calls);row.put("state",RewardReference.state(rng));
                row.put("after_offset",AbstractDungeon.cardBlizzRandomizer);output.add(row);
            }
        }
        ShopScreen screen=(ShopScreen)RewardReference.u.allocateInstance(ShopScreen.class);
        Method init=ShopScreen.class.getDeclaredMethod("initRelics");init.setAccessible(true);
        Field stocks=ShopScreen.class.getDeclaredField("relics");stocks.setAccessible(true);
        stocks.set(screen,new ArrayList<StoreRelic>());
        JsonArray inputs=parser.parse(new String(Files.readAllBytes(Paths.get(args[3])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:inputs) {
            JsonObject row=entry.getAsJsonObject();prepare(row);
            AbstractDungeon.ascensionLevel=row.get("ascension").getAsInt();
            Trace rng=new Trace(row.get("seed").getAsLong());AbstractDungeon.merchantRng=rng;
            if (row.get("kind").getAsString().equals("initial")) {
                init.invoke(screen);
                List<Object> items=new ArrayList<>();
                for (Object value:(List<?>)stocks.get(screen)) {
                    StoreRelic slot=(StoreRelic)value;
                    items.add(Arrays.asList(slot.relic.relicId,slot.price));
                }
                row.add("items",new Gson().toJsonTree(items));
            } else {
                AbstractRelic candidate;
                List<Object> attempts=new ArrayList<>();
                do {
                    AbstractRelic.RelicTier tier=ShopScreen.rollRelicTier();
                    candidate=AbstractDungeon.returnRandomRelicEnd(tier);
                    attempts.add(Arrays.asList(tier.name(),candidate.relicId));
                } while (candidate instanceof OldCoin || candidate instanceof SmilingMask || candidate instanceof MawBank || candidate instanceof Courier);
                AbstractDungeon.player.relics.add(ContentPoolReference.relic("The Courier","UNCOMMON"));
                if (row.get("membership").getAsBoolean()) AbstractDungeon.player.relics.add(ContentPoolReference.relic("Membership Card","SHOP"));
                StoreRelic slot=(StoreRelic)RewardReference.u.allocateInstance(StoreRelic.class);
                slot.price=candidate.getPrice();screen.getNewPrice(slot);
                row.addProperty("result",candidate.relicId);row.addProperty("price",slot.price);
                row.add("attempts",new Gson().toJsonTree(attempts));
            }
            row.add("after",new Gson().toJsonTree(ContentPoolReference.poolState()));
            row.add("calls",new Gson().toJsonTree(rng.calls));row.add("state",new Gson().toJsonTree(RewardReference.state(rng)));
            output.add(row);
        }
        Files.write(Paths.get(args[4]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Merchant protocol rows "+output.size());
    }
}

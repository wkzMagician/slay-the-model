// Actual original canSpawn implementations against explicitly prepared state.
// Draw cases execute original key/noncamp helpers with actual gated relics.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.core.CardCrawlGame;
import com.megacrit.cardcrawl.core.Settings;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.helpers.RelicLibrary;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rooms.*;
import com.google.gson.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

public class RelicSpawnReference {
    static Map<String,JsonObject> relics = new HashMap<>();
    static Map<String,JsonObject> cards = new HashMap<>();
    static Map<String,AbstractRelic> actual = new HashMap<>();

    static AbstractRelic actualRelic(String id) throws Exception {
        if (actual.containsKey(id)) return actual.get(id);
        JsonObject row = relics.get(id);
        Class<?> type = Class.forName("com.megacrit.cardcrawl.relics."+row.get("cls").getAsString());
        AbstractRelic value = (AbstractRelic)RewardReference.u.allocateInstance(type);
        Field identity = AbstractRelic.class.getField("relicId");
        identity.setAccessible(true);
        identity.set(value,id);
        value.tier = AbstractRelic.RelicTier.valueOf(row.get("tier").getAsString());
        actual.put(id,value);
        return value;
    }

    static void prepare(JsonObject row) throws Exception {
        Settings.isEndless = false;
        AbstractDungeon.floorNum = row.get("floor").getAsInt();
        AbstractDungeon.actNum = row.get("act").getAsInt();
        AbstractDungeon.ascensionLevel = row.get("ascension").getAsInt();
        MapRoomNode node = new MapRoomNode(0,0);
        Class<?> room = row.get("shop").getAsBoolean()?ShopRoom.class:MonsterRoom.class;
        node.setRoom((AbstractRoom)RewardReference.u.allocateInstance(room));
        AbstractDungeon.currMapNode = node;
        AbstractDungeon.player.relics.clear();
        for (JsonElement id:row.getAsJsonArray("held")) AbstractDungeon.player.relics.add(actualRelic(id.getAsString()));
        CardGroup deck = new CardGroup(CardGroup.CardGroupType.MASTER_DECK);
        for (JsonElement id:row.getAsJsonArray("deck")) {
            JsonObject metadata = cards.get(id.getAsString());
            AbstractCard card = RewardReference.card(id.getAsString(),AbstractCard.CardRarity.valueOf(metadata.get("rarity").getAsString()));
            card.type = AbstractCard.CardType.valueOf(metadata.get("type").getAsString());
            card.upgraded = row.get("upgraded").getAsBoolean();
            deck.addToTop(card);
        }
        AbstractDungeon.player.masterDeck = deck;
    }

    public static void main(String[] args) throws Exception {
        JsonParser parser = new JsonParser();
        JsonObject catalog = parser.parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject();
        ContentPoolReference.setup(catalog.getAsJsonArray("rows"));
        Field strings = LocalizedStrings.class.getDeclaredField("relics");
        strings.setAccessible(true);
        strings.set(null,new HashMap<String,RelicStrings>() {
            public RelicStrings get(Object id) {
                RelicStrings value = new RelicStrings();
                value.NAME = id.toString(); value.FLAVOR = "prepared";
                value.DESCRIPTIONS = new String[100]; Arrays.fill(value.DESCRIPTIONS,"prepared");
                return value;
            }
        });
        for (JsonElement entry:catalog.getAsJsonArray("rows")) {
            JsonObject row = entry.getAsJsonObject();
            relics.put(row.get("id").getAsString(),row);
        }
        String[] namespaces = {"any","ironclad","silent","defect","watcher"};
        String[] maps = {"sharedRelics","redRelics","greenRelics","blueRelics","purpleRelics"};
        for (JsonObject row:relics.values()) {
            if (row.get("can_spawn_source").isJsonNull()) continue;
            String id = row.get("id").getAsString();
            for (int i=0;i<namespaces.length;i++) {
                if (row.get("namespace").getAsString().equals(namespaces[i])) ContentPoolReference.relicMap(maps[i]).put(id,actualRelic(id));
            }
        }
        JsonArray cardCatalog = parser.parse(new String(Files.readAllBytes(Paths.get(args[1])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:cardCatalog) {
            JsonObject row = entry.getAsJsonObject();
            cards.put(row.get("id").getAsString(),row);
        }
        JsonArray inputs = parser.parse(new String(Files.readAllBytes(Paths.get(args[2])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:inputs) {
            JsonObject row = entry.getAsJsonObject();
            prepare(row);
            ContentPoolReference.Trace rng = new ContentPoolReference.Trace(20261108);
            AbstractDungeon.relicRng = rng;
            if (row.get("category").getAsString().equals("draw")) {
                for (String tier:ContentPoolReference.TIERS) ContentPoolReference.pool(tier).clear();
                String tier = row.get("tier").getAsString();
                for (JsonElement id:row.getAsJsonArray("pool")) ContentPoolReference.pool(tier).add(id.getAsString());
                String result;
                if (row.get("non_campfire").getAsBoolean()) result=AbstractDungeon.returnRandomNonCampfireRelic(AbstractRelic.RelicTier.valueOf(tier)).relicId;
                else if (row.get("shop").getAsBoolean()) result=AbstractDungeon.returnEndRandomRelicKey(AbstractRelic.RelicTier.valueOf(tier));
                else result=AbstractDungeon.returnRandomRelicKey(AbstractRelic.RelicTier.valueOf(tier));
                row.addProperty("result",result);
                row.add("after",new Gson().toJsonTree(ContentPoolReference.poolState()));
            } else {
                row.addProperty("allowed",actualRelic(row.get("key").getAsString()).canSpawn());
            }
            row.add("calls",new Gson().toJsonTree(rng.calls));
            row.add("state",new Gson().toJsonTree(RewardReference.state(rng)));
        }
        Files.write(Paths.get(args[3]),new Gson().toJson(inputs).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Actual original relic eligibility inputs "+inputs.size());
    }
}

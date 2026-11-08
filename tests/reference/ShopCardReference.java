// Source-reconstructed Merchant acceptance loop invoking actual JAR selectors.
// UI construction and pricing are outside this component reference.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.rooms.ShopRoom;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

public class ShopCardReference {
    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        JsonParser parser = new JsonParser();
        SpecialCardReference.pools = parser.parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject().getAsJsonArray("pools");
        JsonArray catalog = parser.parse(new String(Files.readAllBytes(Paths.get(args[1])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:catalog) {
            JsonObject row = entry.getAsJsonObject();
            SpecialCardReference.metadata.put(row.get("id").getAsString(),row);
        }
        MapRoomNode node = new MapRoomNode(0,0);
        node.setRoom(new ShopRoom());
        AbstractDungeon.currMapNode = node;
        List<Object> output = new ArrayList<>();
        for (String color:new String[]{"RED","GREEN","BLUE","PURPLE"}) {
            for (int ascension:new int[]{0,20}) for (int offset:new int[]{5,-40}) for (long seed=0;seed<32;seed++) {
                SpecialCardReference.preparePools(color);
                SpecialCardReference.Trace rng = new SpecialCardReference.Trace(seed);
                AbstractDungeon.cardRng = rng;
                AbstractDungeon.ascensionLevel = ascension;
                AbstractDungeon.cardBlizzRandomizer = offset;
                List<String> ids = new ArrayList<>();
                List<Object> attempts = new ArrayList<>();
                AbstractCard.CardRarity powerRarity = null;
                AbstractCard.CardType[] types = {AbstractCard.CardType.ATTACK,AbstractCard.CardType.ATTACK,AbstractCard.CardType.SKILL,AbstractCard.CardType.SKILL,AbstractCard.CardType.POWER};
                for (int i=0;i<types.length;i++) {
                    AbstractCard c;
                    do {
                        AbstractCard.CardRarity rarity = AbstractDungeon.rollRarity();
                        if (i==4) powerRarity = rarity;
                        c = AbstractDungeon.getCardFromPool(rarity,types[i],true);
                        attempts.add(Arrays.asList(i,rarity.name(),c.cardID));
                    } while (c.color==AbstractCard.CardColor.COLORLESS || ((i==1 || i==3) && Objects.equals(c.cardID,ids.get(i-1))));
                    ids.add(c.cardID);
                }
                ids.add(AbstractDungeon.getColorlessCardFromPool(AbstractCard.CardRarity.UNCOMMON).cardID);
                ids.add(AbstractDungeon.getColorlessCardFromPool(AbstractCard.CardRarity.RARE).cardID);
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("color",color); row.put("ascension",ascension); row.put("offset",offset); row.put("seed",Long.toString(seed));
                row.put("power_fallback",powerRarity==AbstractCard.CardRarity.COMMON);
                row.put("cards",ids);row.put("attempts",attempts);row.put("calls",rng.calls);row.put("state",RewardReference.state(rng));
                row.put("after_offset",AbstractDungeon.cardBlizzRandomizer);
                output.add(row);
            }
        }
        Files.write(Paths.get(args[2]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Source-reconstructed Merchant loop/original selectors cases "+output.size());
    }
}

// Actual original Egg2 preview and obtain hooks against prepared metadata cards.
import com.megacrit.cardcrawl.cards.AbstractCard;
import com.megacrit.cardcrawl.characters.AbstractPlayer;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.google.gson.*;
import java.nio.file.*;
import java.util.*;

public class EggPreviewReference {
    static class PreviewCard extends AbstractCard {
        boolean available;
        int limit;
        private PreviewCard() {
            super("prepared","prepared",null,0,"",CardType.ATTACK,CardColor.RED,CardRarity.COMMON,CardTarget.NONE);
        }
        public boolean canUpgrade() { return available && timesUpgraded<limit; }
        public void upgrade() { upgraded=true;timesUpgraded++; }
        public void use(AbstractPlayer player,AbstractMonster monster) {}
        public AbstractCard makeCopy() { return this; }
    }
    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Map<String,JsonObject> catalog=new HashMap<>();
        JsonArray source=new JsonParser().parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonArray();
        for (JsonElement entry:source) {
            JsonObject row=entry.getAsJsonObject();
            catalog.put(row.get("id").getAsString(),row);
        }
        String[] classes={"MoltenEgg2","ToxicEgg2","FrozenEgg2"};
        String[] keys={"MoltenEgg","ToxicEgg","FrozenEgg"};
        List<Object> output=new ArrayList<>();
        for (int mask=0;mask<8;mask++) {
            List<AbstractRelic> eggs=new ArrayList<>();
            List<String> held=new ArrayList<>();
            for (int index=0;index<classes.length;index++) {
                if ((mask&(1<<index))!=0) {
                    Class<?> type=Class.forName("com.megacrit.cardcrawl.relics."+classes[index]);
                    eggs.add((AbstractRelic)RewardReference.u.allocateInstance(type));
                    held.add(keys[index]);
                }
            }
            for (String id:new String[]{"Anger","Shrug It Off","Corruption","Searing Blow","Flame Barrier","Burn","Injury"}) {
                for (int level=0;level<3;level++) for (boolean available:new boolean[]{false,true}) for (boolean multi:new boolean[]{false,true}) {
                    PreviewCard card=(PreviewCard)RewardReference.u.allocateInstance(PreviewCard.class);
                    card.cardID=id;card.type=AbstractCard.CardType.valueOf(catalog.get(id).get("type").getAsString());
                    card.timesUpgraded=level;card.upgraded=level>0;card.available=available;card.limit=multi?99:1;
                    RewardReference.Trace cardRng=new RewardReference.Trace(11);
                    RewardReference.Trace merchantRng=new RewardReference.Trace(12);
                    AbstractDungeon.cardRng=cardRng;AbstractDungeon.merchantRng=merchantRng;
                    List<Integer> levels=new ArrayList<>();
                    for (int repeat=0;repeat<2;repeat++) {
                        for (AbstractRelic egg:eggs) egg.onPreviewObtainCard(card);
                        levels.add(card.timesUpgraded);
                    }
                    for (AbstractRelic egg:eggs) egg.onObtainCard(card);
                    levels.add(card.timesUpgraded);
                    for (AbstractRelic egg:eggs) egg.onPreviewObtainCard(card);
                    levels.add(card.timesUpgraded);
                    Map<String,Object> row=new LinkedHashMap<>();
                    row.put("held",held);row.put("card",id);row.put("initial_level",level);
                    row.put("available",available);row.put("multi",multi);row.put("levels",levels);
                    row.put("card_state",RewardReference.state(cardRng));row.put("merchant_state",RewardReference.state(merchantRng));
                    row.put("card_calls",cardRng.calls);row.put("merchant_calls",merchantRng.calls);
                    output.add(row);
                }
            }
        }
        Files.write(Paths.get(args[1]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Actual Egg2 preview/obtain component rows "+output.size());
    }
}

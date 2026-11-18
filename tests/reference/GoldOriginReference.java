// Executes original RewardItem creation and AbstractPlayer.gainGold.
// UI/artwork and relic callback bodies are prepared observation boundaries.
import com.badlogic.gdx.math.MathUtils;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rewards.RewardItem;
import com.megacrit.cardcrawl.rooms.*;
import com.google.gson.*;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class GoldOriginReference {
    static List<Integer> callbacks = new ArrayList<>();
    static class Observer extends AbstractRelic {
        private Observer() { super("prepared", "prepared.png", RelicTier.SPECIAL, LandingSound.CLINK); }
        public String getUpdatedDescription() { return "prepared"; }
        public AbstractRelic makeCopy() { return this; }
        public void flash() {}
        public void onGainGold() { if (relicId.equals("observer")) callbacks.add(AbstractDungeon.player.gold); }
    }
    static AbstractRelic relic(String id) throws Exception {
        Observer relic = (Observer) RewardReference.u.allocateInstance(Observer.class);
        java.lang.reflect.Field field = AbstractRelic.class.getField("relicId");
        field.setAccessible(true);
        field.set(relic, id);
        return relic;
    }
    public static void main(String[] args) throws Exception {
        ContentPoolReference.setup(new JsonArray());
        List<Object> rows = new ArrayList<>();
        int[] bases = {-1, 0, 1, 2, 6, 10, 18, 25, 33, 50, 71, 75, 79, 95, 100, 105, 222, 999};
        for (String source : new String[]{"direct", "combat", "event_combat", "treasure", "stolen"}) {
            for (int base : bases) for (boolean idol : new boolean[]{false, true}) for (boolean ectoplasm : new boolean[]{false, true}) {
                AbstractDungeon.player.relics.clear();
                if (idol) AbstractDungeon.player.relics.add(relic("Golden Idol"));
                if (ectoplasm) AbstractDungeon.player.relics.add(relic("Ectoplasm"));
                AbstractDungeon.player.relics.add(relic("observer"));
                AbstractRoom room = source.equals("treasure") ? new TreasureRoom() : source.equals("event_combat") ? new EventRoom() : new MonsterRoom();
                RewardProbabilityReference.room(room);
                int amount = base;
                if (!source.equals("direct")) {
                    RewardItem reward = source.equals("stolen") ? new RewardItem(base, true) : new RewardItem(base);
                    amount = reward.goldAmt + reward.bonusGold;
                }
                AbstractDungeon.player.gold = 100;
                callbacks.clear();
                AbstractDungeon.player.gainGold(amount);
                Map<String,Object> row = new LinkedHashMap<>();
                row.put("source", source); row.put("base", base); row.put("idol", idol); row.put("ectoplasm", ectoplasm);
                row.put("amount", amount); row.put("gold", AbstractDungeon.player.gold); row.put("callbacks", new ArrayList<>(callbacks));
                rows.add(row);
            }
        }
        List<Object> boss = new ArrayList<>();
        for (int base=95; base<=105; base++) for (int asc : new int[]{0,12,13,20}) {
            boss.add(Arrays.asList(base, asc, asc>=13 ? MathUtils.round((float)base*.75f) : base));
        }
        Map<String,Object> result = new LinkedHashMap<>();
        result.put("receipts", rows); result.put("boss_arithmetic", boss);
        Files.write(Paths.get(args[0]), new Gson().toJson(result).getBytes(StandardCharsets.UTF_8));
        System.out.println("Original receipts " + rows.size() + ", source-derived boss arithmetic " + boss.size());
    }
}


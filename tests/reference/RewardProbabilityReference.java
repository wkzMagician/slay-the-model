// Actual original potion reward method and chest open gold calculation.
import com.badlogic.gdx.math.RandomXS128;
import com.megacrit.cardcrawl.audio.SoundMaster;
import com.megacrit.cardcrawl.characters.AbstractPlayer;
import com.megacrit.cardcrawl.core.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.helpers.PotionHelper;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.monsters.MonsterGroup;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rewards.RewardItem;
import com.megacrit.cardcrawl.rewards.chests.AbstractChest;
import com.megacrit.cardcrawl.rooms.*;
import com.megacrit.cardcrawl.screens.CombatRewardScreen;
import com.megacrit.cardcrawl.ui.buttons.ProceedButton;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class RewardProbabilityReference {
    static int capturedGold;

    static class DefeatedMonster extends AbstractMonster {
        DefeatedMonster() { super("prepared", "prepared", 10, 0, 0, 0, 0, null); }
        public void takeTurn() {}
        protected void getMove(int roll) {}
    }

    static class Trace extends ContentPoolReference.Trace {
        Trace(long seed) { super(seed); }
        public float random(float start, float end) {
            float value = super.random(start, end);
            calls.add(Arrays.asList("float_range", start, end, value));
            return value;
        }
    }

    static class FixedFloat extends RandomXS128 {
        float value;
        FixedFloat(float value) { this.value = value; }
        public float nextFloat() { return value; }
    }

    static class RecordingRoom extends TreasureRoom {
        public void addGoldToRewards(int amount) { capturedGold = amount; }
        public void addRelicToRewards(AbstractRelic.RelicTier tier) {}
    }
    static class PreparedChest extends AbstractChest {}
    static class SilentSound extends SoundMaster {
        public long play(String key) { return 0; }
    }
    static class RecordingScreen extends CombatRewardScreen {
        public void open() {}
    }

    static int chestGold(int base, Trace rng) throws Exception {
        AbstractDungeon.treasureRng = rng;
        capturedGold = -1;
        PreparedChest chest = (PreparedChest) RewardReference.u.allocateInstance(PreparedChest.class);
        chest.GOLD_AMT = base;
        chest.goldReward = true;
        chest.relicReward = AbstractChest.RelicReward.COMMON_RELIC;
        chest.open(false);
        return capturedGold;
    }

    static void room(AbstractRoom room) {
        room.rewards = new ArrayList<>();
        MapRoomNode node = new MapRoomNode(0, 0);
        node.setRoom(room);
        AbstractDungeon.currMapNode = node;
    }

    public static void main(String[] args) throws Exception {
        ContentPoolReference.setup(new JsonArray());
        Settings.isDebug = false;
        Settings.isDailyRun = false;
        Settings.isFinalActAvailable = false;
        java.lang.reflect.Field metrics = CardCrawlGame.class.getField("metricData");
        Object data = RewardReference.u.allocateInstance(metrics.getType());
        data.getClass().getField("potions_floor_spawned").set(data, new ArrayList<Integer>());
        metrics.set(null, data);
        CardCrawlGame.sound = (SilentSound) RewardReference.u.allocateInstance(SilentSound.class);
        AbstractDungeon.overlayMenu = (OverlayMenu) RewardReference.u.allocateInstance(OverlayMenu.class);
        AbstractDungeon.overlayMenu.proceedButton = (ProceedButton) RewardReference.u.allocateInstance(ProceedButton.class);
        AbstractDungeon.combatRewardScreen = (RecordingScreen) RewardReference.u.allocateInstance(RecordingScreen.class);
        Gson gson = new GsonBuilder().serializeNulls().create();
        JsonArray inputs = new JsonParser().parse(new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            String kind = row.get("kind").getAsString();
            AbstractDungeon.player.relics.clear();
            if (kind.equals("potion")) {
                AbstractPlayer.PlayerClass role = AbstractPlayer.PlayerClass.valueOf(row.get("role").getAsString());
                AbstractDungeon.player.chosenClass = role;
                PotionHelper.initialize(role);
                if (row.get("statue").getAsBoolean()) {
                    AbstractDungeon.player.relics.add(ContentPoolReference.relic("White Beast Statue", "UNCOMMON"));
                }
                AbstractRoom room = row.get("elite").getAsBoolean() ? new MonsterRoomElite() : new MonsterRoom();
                AbstractMonster defeated = (AbstractMonster) RewardReference.u.allocateInstance(DefeatedMonster.class);
                defeated.currentHealth = 0;
                defeated.isDying = true;
                room.monsters = new MonsterGroup(new AbstractMonster[]{defeated});
                room(room);
                AbstractRoom.blizzardPotionMod = row.get("chance").getAsInt() - 40;
                Trace rng = new Trace(row.get("seed").getAsLong());
                AbstractDungeon.potionRng = rng;
                List<Object> stages = new ArrayList<>();
                for (int step = 0; step < row.get("steps").getAsInt(); step++) {
                    room.rewards.clear();
                    room.addPotionToRewards();
                    String potion = room.rewards.isEmpty() ? null : room.rewards.get(0).potion.ID;
                    stages.add(Arrays.asList(potion, 40 + AbstractRoom.blizzardPotionMod));
                }
                row.add("stages", gson.toJsonTree(stages));
                row.add("calls", gson.toJsonTree(rng.calls));
                row.add("state", gson.toJsonTree(RewardReference.state(rng)));
            } else {
                room((RecordingRoom) RewardReference.u.allocateInstance(RecordingRoom.class));
                int base = row.get("base").getAsInt();
                if (kind.equals("gold")) {
                    Trace rng = new Trace(row.get("seed").getAsLong());
                    row.addProperty("gold", chestGold(base, rng));
                    row.add("calls", gson.toJsonTree(rng.calls));
                    row.add("state", gson.toJsonTree(RewardReference.state(rng)));
                } else {
                    List<Integer> values = new ArrayList<>();
                    for (JsonElement input : row.getAsJsonArray("inputs")) {
                        Trace rng = new Trace(0);
                        rng.random = new FixedFloat(input.getAsFloat());
                        values.add(chestGold(base, rng));
                    }
                    row.add("values", gson.toJsonTree(values));
                }
            }
            output.add(row);
        }
        Files.write(Paths.get(args[1]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual reward probability component rows " + output.size());
    }
}

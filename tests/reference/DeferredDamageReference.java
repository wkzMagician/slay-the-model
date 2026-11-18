// Actual original deferred target actions; damage/render boundaries are recorded.
import com.megacrit.cardcrawl.actions.AbstractGameAction;
import com.megacrit.cardcrawl.actions.GameActionManager;
import com.megacrit.cardcrawl.actions.common.DamageAction;
import com.megacrit.cardcrawl.actions.common.DamageAllEnemiesAction;
import com.megacrit.cardcrawl.actions.common.DamageRandomEnemyAction;
import com.megacrit.cardcrawl.actions.defect.LightningOrbPassiveAction;
import com.megacrit.cardcrawl.actions.defect.LightningOrbEvokeAction;
import com.megacrit.cardcrawl.cards.DamageInfo;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.monsters.MonsterGroup;
import com.megacrit.cardcrawl.powers.AbstractPower;
import com.megacrit.cardcrawl.rooms.MonsterRoom;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class DeferredDamageReference {
    static class PreparedMonster extends AbstractMonster {
        PreparedMonster() { super("prepared", "prepared", 100, 0, 0, 0, 0, null); }
        public void takeTurn() {}
        protected void getMove(int roll) {}
    }

    static class PreparedPower extends AbstractPower {}

    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public int random(int start, int end) {
            int value = super.random(start, end);
            calls.add(Arrays.asList("int_range", start, end, value));
            return value;
        }
    }

    // The original target actions enqueue actual DamageAction objects. This
    // adapter records their parameters and advances explicit HP/block state.
    // Monster.damage, reactions, render and animation actions are outside scope.
    static void recordDamage(AbstractMonster target, int damage, List<AbstractMonster> monsters, List<Object> hits) {
        if (target.currentHealth <= 0 || target.halfDead || target.isEscaping || target.isDying) return;
        hits.add(Arrays.asList(monsters.indexOf(target), damage));
        int absorbed = Math.min(target.currentBlock, damage);
        target.currentBlock -= absorbed;
        target.currentHealth = Math.max(0, target.currentHealth - damage + absorbed);
        if (target.currentHealth == 0) target.isDying = true;
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        com.badlogic.gdx.graphics.g2d.TextureAtlas.AtlasRegion region =
            new com.badlogic.gdx.graphics.g2d.TextureAtlas.AtlasRegion(
                com.megacrit.cardcrawl.helpers.ImageMaster.WHITE_SQUARE_IMG, 0, 0, 64, 64
            );
        com.megacrit.cardcrawl.helpers.ImageMaster.vfxAtlas = new com.badlogic.gdx.graphics.g2d.TextureAtlas() {
            public AtlasRegion findRegion(String name) { return region; }
        };
        AbstractDungeon.player.orbs = new ArrayList<>();
        AbstractDungeon.player.powers = new ArrayList<>();
        Gson gson = new Gson();
        JsonArray inputs = new JsonParser().parse(
            new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        java.lang.reflect.Field infoField = DamageAction.class.getDeclaredField("info");
        infoField.setAccessible(true);
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            List<AbstractMonster> monsters = new ArrayList<>();
            for (JsonElement value : row.getAsJsonArray("enemies")) {
                JsonObject input = value.getAsJsonObject();
                AbstractMonster monster = (AbstractMonster) RewardReference.u.allocateInstance(PreparedMonster.class);
                monster.currentHealth = input.get("hp").getAsInt();
                monster.currentBlock = input.get("block").getAsInt();
                monster.isDying = input.get("dying").getAsBoolean();
                monster.isEscaping = input.get("escaping").getAsBoolean();
                monster.halfDead = input.get("half_dead").getAsBoolean();
                monster.powers = new ArrayList<>();
                if (input.get("lock").getAsBoolean()) {
                    AbstractPower lock = (AbstractPower) RewardReference.u.allocateInstance(PreparedPower.class);
                    lock.ID = "Lockon";
                    lock.amount = 1;
                    monster.powers.add(lock);
                }
                monsters.add(monster);
            }
            MonsterRoom room = new MonsterRoom();
            room.monsters = new MonsterGroup(monsters.toArray(new AbstractMonster[0]));
            MapRoomNode node = new MapRoomNode(0, 0);
            node.setRoom(room);
            AbstractDungeon.currMapNode = node;
            GameActionManager manager = (GameActionManager) RewardReference.u.allocateInstance(GameActionManager.class);
            manager.actions = new ArrayList<>();
            AbstractDungeon.actionManager = manager;
            Trace rng = new Trace(row.get("seed").getAsLong());
            AbstractDungeon.cardRandomRng = rng;
            int damage = row.get("damage").getAsInt();
            String kind = row.get("kind").getAsString();
            boolean all = row.get("hit_all").getAsBoolean();
            if (row.get("pre_damage").getAsInt() > 0) {
                manager.addToBottom(new DamageAction(monsters.get(0), new DamageInfo(
                    AbstractDungeon.player, row.get("pre_damage").getAsInt(), DamageInfo.DamageType.THORNS
                )));
            }
            for (int count = 0; count < row.get("count").getAsInt(); count++) {
                DamageInfo info = new DamageInfo(AbstractDungeon.player, damage, DamageInfo.DamageType.THORNS);
                if (kind.equals("juggernaut")) {
                    manager.addToBottom(new DamageRandomEnemyAction(info, AbstractGameAction.AttackEffect.NONE));
                } else if (kind.equals("passive")) {
                    manager.addToBottom(new LightningOrbPassiveAction(info, null, all));
                } else {
                    manager.addToBottom(new LightningOrbEvokeAction(info, all));
                }
            }
            List<Object> hits = new ArrayList<>();
            while (!manager.actions.isEmpty()) {
                AbstractGameAction action = manager.actions.remove(0);
                if (action instanceof DamageAction) {
                    DamageInfo info = (DamageInfo) infoField.get(action);
                    recordDamage((AbstractMonster) action.target, info.output, monsters, hits);
                } else if (action instanceof DamageAllEnemiesAction) {
                    int[] matrix = ((DamageAllEnemiesAction) action).damage;
                    for (int index = 0; index < monsters.size(); index++) {
                        recordDamage(monsters.get(index), matrix[index], monsters, hits);
                    }
                } else if (action instanceof DamageRandomEnemyAction
                        || action instanceof LightningOrbPassiveAction || action instanceof LightningOrbEvokeAction) {
                    action.update();
                }
            }
            List<Integer> health = new ArrayList<>();
            List<Integer> blocks = new ArrayList<>();
            for (AbstractMonster monster : monsters) {
                health.add(monster.currentHealth);
                blocks.add(monster.currentBlock);
            }
            row.add("hits", gson.toJsonTree(hits));
            row.add("health", gson.toJsonTree(health));
            row.add("blocks", gson.toJsonTree(blocks));
            row.add("calls", gson.toJsonTree(rng.calls));
            row.add("state", gson.toJsonTree(RewardReference.state(rng)));
            output.add(row);
        }
        Files.write(Paths.get(args[1]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual deferred damage action component rows " + output.size());
    }
}

// Actual original insertion and active-shuffle actions with a Soul boundary.
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Graphics;
import com.megacrit.cardcrawl.actions.AbstractGameAction;
import com.megacrit.cardcrawl.actions.GameActionManager;
import com.megacrit.cardcrawl.actions.common.EmptyDeckShuffleAction;
import com.megacrit.cardcrawl.actions.common.ShuffleAction;
import com.megacrit.cardcrawl.actions.defect.ShuffleAllAction;
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.helpers.TipTracker;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rooms.MonsterRoom;
import com.megacrit.cardcrawl.screens.select.HandCardSelectScreen;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class ShuffleInsertionReference {
    static List<Object> moves;
    static List<Object> notices;
    static RewardReference.Trace cardRng;
    static Trace shuffleRng;

    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public long randomLong() {
            long value = super.randomLong();
            calls.add(Arrays.asList("long", Long.toString(value)));
            return value;
        }
    }

    static class RecordingRelic extends AbstractRelic {
        RecordingRelic() { super("prepared", "prepared", RelicTier.COMMON, LandingSound.SOLID); }
        public String getUpdatedDescription() { return "prepared"; }
        public AbstractRelic makeCopy() { return this; }
        public void onShuffle() {
            notices.add(Arrays.asList(cardRng.counter, shuffleRng.counter));
        }
    }

    // Original actions remove cards; this animation boundary performs the
    // original immediate addToTop operation and records transfer order.
    static class RecordingSouls extends SoulGroup {
        public void shuffle(AbstractCard card, boolean invisible) {
            AbstractDungeon.player.drawPile.addToTop(card);
            moves.add(Arrays.asList("discard", card.cardID));
        }
        public void onToDeck(AbstractCard card, boolean randomSpot) {
            if (randomSpot) throw new IllegalStateException("Unexpected random placement");
            AbstractDungeon.player.drawPile.addToTop(card);
            moves.add(Arrays.asList("hand", card.cardID));
        }
    }

    static CardGroup group(String prefix, int count, CardGroup.CardGroupType type) throws Exception {
        CardGroup group = new CardGroup(type);
        java.lang.reflect.Field glows = AbstractCard.class.getDeclaredField("glowList");
        glows.setAccessible(true);
        for (int index = 0; index < count; index++) {
            AbstractCard card = RewardReference.card(prefix + index, AbstractCard.CardRarity.COMMON);
            glows.set(card, new ArrayList<>());
            group.group.add(card);
        }
        return group;
    }

    static List<String> ids(CardGroup group) {
        List<String> ids = new ArrayList<>();
        for (AbstractCard card : group.group) ids.add(card.cardID);
        return ids;
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Graphics previous = Gdx.graphics;
        Gdx.graphics = (Graphics) java.lang.reflect.Proxy.newProxyInstance(
            ShuffleInsertionReference.class.getClassLoader(), new Class[]{Graphics.class},
            (proxy, method, values) -> method.getName().equals("getDeltaTime") ? 0.01f : method.invoke(previous, values)
        );
        TipTracker.tips = new HashMap<>();
        TipTracker.tips.put("SHUFFLE_TIP", true);
        AbstractDungeon.handCardSelectScreen = (HandCardSelectScreen) RewardReference.u.allocateInstance(HandCardSelectScreen.class);
        AbstractDungeon.handCardSelectScreen.wereCardsRetrieved = true;
        Gson gson = new Gson();
        JsonArray inputs = new JsonParser().parse(
            new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            long seed = row.get("seed").getAsLong();
            cardRng = new RewardReference.Trace(seed);
            shuffleRng = new Trace(seed + 1);
            AbstractDungeon.cardRandomRng = cardRng;
            AbstractDungeon.shuffleRng = shuffleRng;
            moves = new ArrayList<>();
            notices = new ArrayList<>();
            String kind = row.get("kind").getAsString();
            if (kind.equals("insert")) {
                CardGroup pile = group("I", row.get("size").getAsInt(), CardGroup.CardGroupType.DRAW_PILE);
                List<Object> stages = new ArrayList<>();
                for (int index = 0; index < row.get("count").getAsInt(); index++) {
                    pile.addToRandomSpot(RewardReference.card("N" + index, AbstractCard.CardRarity.COMMON));
                    stages.add(ids(pile));
                }
                row.add("stages", gson.toJsonTree(stages));
            } else {
                AbstractDungeon.player.drawPile = group("D", row.get("draw").getAsInt(), CardGroup.CardGroupType.DRAW_PILE);
                AbstractDungeon.player.discardPile = group("C", row.get("discard").getAsInt(), CardGroup.CardGroupType.DISCARD_PILE);
                AbstractDungeon.player.hand = group("H", row.get("hand").getAsInt(), CardGroup.CardGroupType.HAND);
                AbstractDungeon.player.relics.clear();
                AbstractDungeon.player.relics.add((RecordingRelic) RewardReference.u.allocateInstance(RecordingRelic.class));
                MonsterRoom room = new MonsterRoom();
                room.souls = (RecordingSouls) RewardReference.u.allocateInstance(RecordingSouls.class);
                MapRoomNode node = new MapRoomNode(0, 0);
                node.setRoom(room);
                AbstractDungeon.currMapNode = node;
                GameActionManager manager = (GameActionManager) RewardReference.u.allocateInstance(GameActionManager.class);
                manager.actions = new ArrayList<>();
                manager.cardQueue = new ArrayList<>();
                AbstractDungeon.actionManager = manager;
                if (kind.equals("reboot")) {
                    manager.addToBottom(new ShuffleAllAction());
                    manager.addToBottom(new ShuffleAction(AbstractDungeon.player.drawPile, false));
                } else if (row.get("discard").getAsInt() > 0) {
                    manager.addToBottom(new EmptyDeckShuffleAction());
                    manager.addToBottom(new ShuffleAction(AbstractDungeon.player.drawPile, false));
                }
                List<Object> stages = new ArrayList<>();
                while (!manager.actions.isEmpty()) {
                    AbstractGameAction action = manager.actions.remove(0);
                    int frames = 0;
                    while (!action.isDone && frames++ < 200) action.update();
                    if (!action.isDone) throw new IllegalStateException("Action failed to complete");
                    stages.add(Arrays.asList(action.getClass().getSimpleName(), ids(AbstractDungeon.player.drawPile), ids(AbstractDungeon.player.hand)));
                }
                row.add("stages", gson.toJsonTree(stages));
                row.add("draw_after", gson.toJsonTree(ids(AbstractDungeon.player.drawPile)));
                row.add("hand_after", gson.toJsonTree(ids(AbstractDungeon.player.hand)));
                row.add("discard_after", gson.toJsonTree(ids(AbstractDungeon.player.discardPile)));
                row.add("moves", gson.toJsonTree(moves));
                row.add("notices", gson.toJsonTree(notices));
            }
            row.add("card_calls", gson.toJsonTree(cardRng.calls));
            row.add("shuffle_calls", gson.toJsonTree(shuffleRng.calls));
            row.add("card_state", gson.toJsonTree(RewardReference.state(cardRng)));
            row.add("shuffle_state", gson.toJsonTree(RewardReference.state(shuffleRng)));
            output.add(row);
        }
        Files.write(Paths.get(args[1]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual shuffle/insertion component rows " + output.size());
    }
}

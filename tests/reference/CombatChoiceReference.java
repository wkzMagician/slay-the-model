// Actual original action updates with prepared cards, pools and UI boundary.
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.Graphics;
import com.megacrit.cardcrawl.actions.unique.DiscoveryAction;
import com.megacrit.cardcrawl.actions.unique.MadnessAction;
import com.megacrit.cardcrawl.cards.AbstractCard;
import com.megacrit.cardcrawl.cards.CardGroup;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.helpers.CardLibrary;
import com.megacrit.cardcrawl.screens.CardRewardScreen;
import com.google.gson.*;
import java.lang.reflect.Proxy;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class CombatChoiceReference {
    static class RecordingScreen extends CardRewardScreen {
        boolean skippableValue;
        ArrayList<AbstractCard> generated;

        public void customCombatOpen(ArrayList<AbstractCard> cards, String text, boolean skippable) {
            generated = cards;
            skippableValue = skippable;
        }
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Graphics previous = Gdx.graphics;
        Gdx.graphics = (Graphics) Proxy.newProxyInstance(
            CombatChoiceReference.class.getClassLoader(), new Class[]{Graphics.class},
            (proxy, method, values) -> {
                if (method.getName().equals("getDeltaTime")) return 0.01f;
                return method.invoke(previous, values);
            }
        );
        JsonParser parser = new JsonParser();
        Gson gson = new GsonBuilder().serializeNulls().create();
        JsonArray inputs = parser.parse(
            new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            CardGroup hand = new CardGroup(CardGroup.CardGroupType.HAND);
            for (JsonElement value : row.getAsJsonArray("hand")) {
                JsonObject input = value.getAsJsonObject();
                AbstractCard card = RewardReference.card(
                    Integer.toString(hand.size()), AbstractCard.CardRarity.COMMON
                );
                card.cost = input.get("cost").getAsInt();
                card.costForTurn = input.get("turn").isJsonNull()
                    ? card.cost : input.get("turn").getAsInt();
                card.freeToPlayOnce = input.get("free").getAsBoolean();
                hand.group.add(card);
            }
            AbstractDungeon.player.hand = hand;
            RewardReference.Trace rng = new RewardReference.Trace(row.get("seed").getAsLong());
            AbstractDungeon.cardRandomRng = rng;
            new MadnessAction().update();
            List<Object> after = new ArrayList<>();
            Integer target = null;
            for (int index = 0; index < hand.size(); index++) {
                AbstractCard card = hand.group.get(index);
                if (card.isCostModified) target = index;
                after.add(Arrays.asList(card.cost, card.costForTurn, card.freeToPlayOnce));
            }
            row.addProperty("kind", "madness");
            row.add("target", gson.toJsonTree(target));
            row.add("after", gson.toJsonTree(after));
            row.add("calls", gson.toJsonTree(rng.calls));
            row.add("state", gson.toJsonTree(RewardReference.state(rng)));
            output.add(row);
        }
        SpecialCardReference.pools = parser.parse(
            new String(Files.readAllBytes(Paths.get(args[1])), StandardCharsets.UTF_8)
        ).getAsJsonObject().getAsJsonArray("pools");
        CardLibrary.cards.clear();
        JsonArray catalog = parser.parse(
            new String(Files.readAllBytes(Paths.get(args[2])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        for (JsonElement entry : catalog) {
            JsonObject row = entry.getAsJsonObject();
            SpecialCardReference.metadata.put(row.get("id").getAsString(), row);
        }
        for (String id : SpecialCardReference.metadata.keySet()) {
            CardLibrary.cards.put(id, SpecialCardReference.card(id));
        }
        for (String color : new String[]{"RED", "GREEN", "BLUE", "PURPLE"}) {
            for (String variant : new String[]{"default", "ATTACK", "SKILL", "POWER"}) {
                for (long seed : new long[]{0, 42, 20261112}) {
                    SpecialCardReference.preparePools(color);
                    SpecialCardReference.Trace rng = new SpecialCardReference.Trace(seed);
                    AbstractDungeon.cardRandomRng = rng;
                    AbstractDungeon.cardRng = new RewardReference.Trace(seed + 1);
                    RecordingScreen screen = (RecordingScreen) RewardReference.u.allocateInstance(RecordingScreen.class);
                    AbstractDungeon.cardRewardScreen = screen;
                    DiscoveryAction action = variant.equals("default")
                        ? new DiscoveryAction() : new DiscoveryAction(AbstractCard.CardType.valueOf(variant), 1);
                    action.update();
                    Map<String, Object> row = new LinkedHashMap<>();
                    row.put("kind", "discovery");
                    row.put("color", color);
                    row.put("variant", variant);
                    row.put("seed", Long.toString(seed));
                    row.put("skippable", screen.skippableValue);
                    List<String> ids = new ArrayList<>();
                    for (AbstractCard card : screen.generated) ids.add(card.cardID);
                    row.put("cards", ids);
                    row.put("calls", rng.calls);
                    row.put("state", RewardReference.state(rng));
                    output.add(row);
                }
            }
        }
        Files.write(Paths.get(args[3]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual combat-choice component rows " + output.size());
    }
}

// Actual original ConfusionPower callback, orb helper and hand-cost action.
import com.megacrit.cardcrawl.cards.AbstractCard;
import com.megacrit.cardcrawl.cards.CardGroup;
import com.megacrit.cardcrawl.core.CardCrawlGame;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.orbs.AbstractOrb;
import com.megacrit.cardcrawl.powers.ConfusionPower;
import com.megacrit.cardcrawl.actions.unique.RandomizeHandCostAction;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class ChaosConfusionReference {
    static AbstractCard card(JsonObject input) {
        AbstractCard card = RewardReference.card("prepared", AbstractCard.CardRarity.COMMON);
        card.cost = input.get("cost").getAsInt();
        card.costForTurn = input.get("turn").isJsonNull() ? card.cost : input.get("turn").getAsInt();
        card.freeToPlayOnce = input.get("free").getAsBoolean();
        return card;
    }

    static List<Object> values(AbstractCard card) {
        return Arrays.asList(card.cost, card.costForTurn, card.freeToPlayOnce);
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        java.lang.reflect.Field powers = LocalizedStrings.class.getDeclaredField("powers");
        powers.setAccessible(true);
        powers.set(null, new HashMap<String, PowerStrings>() {
            public PowerStrings get(Object key) {
                PowerStrings value = new PowerStrings();
                value.NAME = "prepared";
                value.DESCRIPTIONS = new String[]{"prepared"};
                return value;
            }
        });
        java.lang.reflect.Field orbs = LocalizedStrings.class.getDeclaredField("orb");
        orbs.setAccessible(true);
        orbs.set(null, new HashMap<String, OrbStrings>() {
            public OrbStrings get(Object key) {
                OrbStrings value = new OrbStrings();
                value.NAME = "prepared";
                value.DESCRIPTION = new String[10];
                Arrays.fill(value.DESCRIPTION, "prepared");
                return value;
            }
        });
        AbstractDungeon.player.powers = new ArrayList<>();
        ConfusionPower power = (ConfusionPower) RewardReference.u.allocateInstance(ConfusionPower.class);
        Gson gson = new GsonBuilder().serializeNulls().create();
        JsonArray inputs = new JsonParser().parse(
            new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            RewardReference.Trace rng = new RewardReference.Trace(row.get("seed").getAsLong());
            AbstractDungeon.cardRandomRng = rng;
            String kind = row.get("kind").getAsString();
            if (kind.equals("confusion")) {
                AbstractCard card = card(row);
                List<Object> stages = new ArrayList<>();
                for (int index = 0; index < row.get("repeats").getAsInt(); index++) {
                    power.onCardDraw(card);
                    stages.add(values(card));
                }
                row.add("stages", gson.toJsonTree(stages));
            } else if (kind.equals("chaos")) {
                List<String> selected = new ArrayList<>();
                for (int index = 0; index < row.get("count").getAsInt(); index++) {
                    selected.add(AbstractOrb.getRandomOrb(true).getClass().getSimpleName());
                }
                row.add("orbs", gson.toJsonTree(selected));
            } else {
                CardGroup hand = new CardGroup(CardGroup.CardGroupType.HAND);
                for (JsonElement input : row.getAsJsonArray("existing")) hand.group.add(card(input.getAsJsonObject()));
                List<Object> afterDraw = new ArrayList<>();
                for (JsonElement input : row.getAsJsonArray("drawn")) {
                    AbstractCard drawn = card(input.getAsJsonObject());
                    hand.group.add(drawn);
                    power.onCardDraw(drawn);
                    afterDraw.add(values(drawn));
                }
                row.add("draw_stages", gson.toJsonTree(afterDraw));
                AbstractDungeon.player.hand = hand;
                new RandomizeHandCostAction().update();
                List<Object> afterOil = new ArrayList<>();
                for (AbstractCard value : hand.group) afterOil.add(values(value));
                row.add("after_oil", gson.toJsonTree(afterOil));
            }
            row.add("calls", gson.toJsonTree(rng.calls));
            row.add("state", gson.toJsonTree(RewardReference.state(rng)));
            output.add(row);
        }
        Files.write(Paths.get(args[1]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual chaos/confusion component rows " + output.size());
    }
}

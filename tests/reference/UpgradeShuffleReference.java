// Executes actual WarPaint/Whetstone onEquip with prepared metadata cards.
import com.megacrit.cardcrawl.cards.AbstractCard;
import com.megacrit.cardcrawl.cards.CardGroup;
import com.megacrit.cardcrawl.characters.AbstractPlayer;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.google.gson.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

public class UpgradeShuffleReference {
    static List<Integer> upgradeOrder;

    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public long randomLong() {
            long value = super.randomLong();
            calls.add(Arrays.asList("long", Long.toString(value)));
            return value;
        }
    }

    static class PreparedCard extends AbstractCard {
        int slot;
        int limit;
        boolean available;
        boolean tracked;

        private PreparedCard() {
            super("prepared", "prepared", null, 0, "", CardType.ATTACK,
                  CardColor.RED, CardRarity.COMMON, CardTarget.NONE);
        }
        public boolean canUpgrade() { return available && timesUpgraded < limit; }
        public void upgrade() {
            upgraded = true;
            timesUpgraded++;
            name = cardID + "+" + timesUpgraded;
            if (tracked) upgradeOrder.add(slot);
        }
        public void use(AbstractPlayer player, AbstractMonster monster) {}
        public AbstractCard makeCopy() {
            try {
                PreparedCard copy = (PreparedCard) RewardReference.u.allocateInstance(PreparedCard.class);
                copy.cardID = cardID;
                copy.type = type;
                copy.color = color;
                copy.name = cardID;
                copy.available = available;
                copy.limit = limit;
                return copy;
            } catch (Exception error) {
                throw new RuntimeException(error);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Gson gson = new Gson();
        JsonArray inputs = new JsonParser().parse(
            new String(Files.readAllBytes(Paths.get(args[0])), StandardCharsets.UTF_8)
        ).getAsJsonArray();
        List<Object> output = new ArrayList<>();
        for (JsonElement entry : inputs) {
            JsonObject row = entry.getAsJsonObject();
            CardGroup deck = new CardGroup(CardGroup.CardGroupType.MASTER_DECK);
            for (JsonElement value : row.getAsJsonArray("deck")) {
                JsonObject input = value.getAsJsonObject();
                PreparedCard card = (PreparedCard) RewardReference.u.allocateInstance(PreparedCard.class);
                card.slot = deck.size();
                card.cardID = input.get("id").getAsString();
                card.name = card.cardID;
                card.type = AbstractCard.CardType.valueOf(input.get("type").getAsString());
                card.color = AbstractCard.CardColor.valueOf(input.get("color").getAsString());
                card.timesUpgraded = input.get("level").getAsInt();
                card.upgraded = card.timesUpgraded > 0;
                card.limit = input.get("limit").getAsInt();
                card.available = input.get("available").getAsBoolean();
                boolean bottled = input.get("bottled").getAsBoolean();
                card.inBottleFlame = bottled && card.type == AbstractCard.CardType.ATTACK;
                card.inBottleLightning = bottled && card.type == AbstractCard.CardType.SKILL;
                card.tracked = true;
                deck.group.add(card);
            }
            AbstractDungeon.player.masterDeck = deck;
            AbstractDungeon.player.relics.clear();
            AbstractDungeon.effectList.clear();
            AbstractDungeon.topLevelEffects.clear();
            Trace rng = new Trace(row.get("seed").getAsLong());
            AbstractDungeon.miscRng = rng;
            upgradeOrder = new ArrayList<>();
            Class<?> type = Class.forName("com.megacrit.cardcrawl.relics." + row.get("relic").getAsString());
            AbstractRelic relic = (AbstractRelic) RewardReference.u.allocateInstance(type);
            relic.onEquip();
            List<Integer> levels = new ArrayList<>();
            List<Boolean> flags = new ArrayList<>();
            for (AbstractCard card : deck.group) {
                levels.add(card.timesUpgraded);
                flags.add(card.inBottleFlame || card.inBottleLightning);
            }
            row.add("levels", gson.toJsonTree(levels));
            row.add("bottled", gson.toJsonTree(flags));
            row.add("upgrade_order", gson.toJsonTree(upgradeOrder));
            row.add("calls", gson.toJsonTree(rng.calls));
            row.add("state", gson.toJsonTree(RewardReference.state(rng)));
            row.addProperty("effects", AbstractDungeon.topLevelEffects.size());
            output.add(row);
        }
        Files.write(Paths.get(args[1]), gson.toJson(output).getBytes(StandardCharsets.UTF_8));
        System.out.println("Actual upgrade relic onEquip rows " + output.size());
    }
}

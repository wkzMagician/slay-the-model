// Actual fixed-JAR selection methods with prepared metadata cards and pools.
// The Library loop is reconstructed from source and calls original JAR helpers.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.actions.unique.DiscoveryAction;
import com.megacrit.cardcrawl.actions.watcher.ForeignInfluenceAction;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.helpers.CardLibrary;
import com.megacrit.cardcrawl.neow.*;
import com.google.gson.*;
import java.util.*;
import java.nio.file.*;
import java.lang.reflect.Method;

public class SpecialCardReference {
    static Map<String, JsonObject> metadata = new HashMap<>();
    static JsonArray pools;

    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public boolean randomBoolean(float chance) {
            boolean value = super.randomBoolean(chance);
            calls.set(calls.size() - 1, Arrays.asList("boolean", (double)chance, value));
            return value;
        }
        public long randomLong() {
            long value = super.randomLong();
            calls.add(Arrays.asList("long", Long.toString(value)));
            return value;
        }
        public int random(int start, int end) {
            int value = super.random(start, end);
            calls.add(Arrays.asList("int_range", start, end, value));
            return value;
        }
    }

    static AbstractCard card(String id) {
        JsonObject row = metadata.get(id);
        AbstractCard result = RewardReference.card(id, AbstractCard.CardRarity.valueOf(row.get("rarity").getAsString()));
        result.type = AbstractCard.CardType.valueOf(row.get("type").getAsString());
        result.color = AbstractCard.CardColor.valueOf(row.get("color").getAsString());
        result.tags = new ArrayList<>();
        if (row.get("healing").getAsBoolean()) result.tags.add(AbstractCard.CardTags.HEALING);
        result.isSeen = true;
        return result;
    }

    static CardGroup group(JsonArray ids) {
        CardGroup result = new CardGroup(CardGroup.CardGroupType.CARD_POOL);
        for (JsonElement id : ids) result.addToTop(card(id.getAsString()));
        return result;
    }

    static void preparePools(String color) {
        for (JsonElement entry : pools) {
            JsonObject row = entry.getAsJsonObject();
            String poolColor = row.get("color").getAsString();
            if (poolColor.equals("COLORLESS")) {
                AbstractDungeon.colorlessCardPool = group(row.getAsJsonArray("initialized"));
                AbstractDungeon.srcColorlessCardPool = group(row.getAsJsonArray("source_copy"));
            } else if (poolColor.equals(color)) {
                CardGroup current = group(row.getAsJsonArray("initialized"));
                CardGroup source = group(row.getAsJsonArray("source_copy"));
                switch (row.get("rarity").getAsString()) {
                    case "COMMON": AbstractDungeon.commonCardPool = current; AbstractDungeon.srcCommonCardPool = source; break;
                    case "UNCOMMON": AbstractDungeon.uncommonCardPool = current; AbstractDungeon.srcUncommonCardPool = source; break;
                    case "RARE": AbstractDungeon.rareCardPool = current; AbstractDungeon.srcRareCardPool = source; break;
                    default: throw new IllegalArgumentException();
                }
            }
        }
    }

    static Object invoke(Class<?> owner, String name, Class<?>[] types, Object... args) throws Exception {
        Method method = owner.getDeclaredMethod(name, types);
        method.setAccessible(true);
        return method.invoke(RewardReference.u.allocateInstance(owner), args);
    }

    static List<AbstractCard> libraryLoop() {
        List<AbstractCard> result = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        while (result.size() < 20) {
            AbstractCard candidate = AbstractDungeon.getCard(AbstractDungeon.rollRarity()).makeCopy();
            if (seen.add(candidate.cardID)) result.add(0, candidate);
        }
        return result;
    }

    @SuppressWarnings("unchecked")
    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        JsonParser parser = new JsonParser();
        pools = parser.parse(new String(Files.readAllBytes(Paths.get(args[0])), "UTF-8")).getAsJsonObject().getAsJsonArray("pools");
        JsonArray catalog = parser.parse(new String(Files.readAllBytes(Paths.get(args[1])), "UTF-8")).getAsJsonArray();
        for (JsonElement entry : catalog) {
            JsonObject row = entry.getAsJsonObject();
            metadata.put(row.get("id").getAsString(), row);
        }
        CardLibrary.cards.clear();
        java.lang.reflect.Field curseField = CardLibrary.class.getDeclaredField("curses");
        curseField.setAccessible(true);
        Map<String,AbstractCard> curses = (Map<String,AbstractCard>)curseField.get(null);
        curses.clear();
        for (JsonElement entry : catalog) {
            String id = entry.getAsJsonObject().get("id").getAsString();
            AbstractCard value = card(id);
            CardLibrary.cards.put(id, value);
            if (value.color == AbstractCard.CardColor.CURSE) curses.put(id, value);
        }
        List<Object> output = new ArrayList<>();
        String[] protocols = {"discovery", "colorless_discovery", "foreign", "neow_colorless", "neow_rare_colorless", "neow_colored", "neow_rare_colored", "library", "transform_Anger", "transform_Strike_R", "transform_Finesse", "transform_Injury", "transform_Unload"};
        for (String color : new String[]{"RED", "GREEN", "BLUE", "PURPLE"}) {
            for (long seed : new long[]{0, 1, 42, 999, -1, 20261106}) {
                for (String protocol : protocols) {
                    preparePools(color);
                    boolean mutated = seed == 42;
                    if (mutated) AbstractDungeon.commonCardPool.group.remove(0);
                    Trace cardRng = new Trace(seed + 1), randomRng = new Trace(seed + 2);
                    Trace neowRng = new Trace(seed), miscRng = new Trace(seed + 3);
                    AbstractDungeon.cardRng = cardRng;
                    AbstractDungeon.cardRandomRng = randomRng;
                    NeowEvent.rng = neowRng;
                    AbstractDungeon.cardBlizzRandomizer = seed == -1 ? -40 : 5;
                    AbstractDungeon.currMapNode = null;
                    List<AbstractCard> cards;
                    if (protocol.equals("discovery")) {
                        cards = (List<AbstractCard>)invoke(DiscoveryAction.class, "generateCardChoices", new Class[]{AbstractCard.CardType.class}, (Object)null);
                    } else if (protocol.equals("colorless_discovery")) {
                        cards = (List<AbstractCard>)invoke(DiscoveryAction.class, "generateColorlessCardChoices", new Class[]{});
                    } else if (protocol.equals("foreign")) {
                        cards = (List<AbstractCard>)invoke(ForeignInfluenceAction.class, "generateCardChoices", new Class[]{});
                    } else if (protocol.startsWith("neow_")) {
                        NeowReward reward = (NeowReward)RewardReference.u.allocateInstance(NeowReward.class);
                        boolean rare = protocol.contains("rare");
                        cards = protocol.endsWith("colorless") ? reward.getColorlessRewardCards(rare) : reward.getRewardCards(rare);
                    } else if (protocol.equals("library")) {
                        cards = libraryLoop();
                    } else {
                        AbstractCard old = card(protocol.substring("transform_".length()));
                        AbstractCard changed;
                        if (old.color == AbstractCard.CardColor.CURSE) changed = CardLibrary.getCurse(old, miscRng);
                        else if (old.color == AbstractCard.CardColor.COLORLESS) changed = AbstractDungeon.returnTrulyRandomColorlessCardFromAvailable(old, miscRng);
                        else changed = AbstractDungeon.returnTrulyRandomCardFromAvailable(old, miscRng);
                        cards = Arrays.asList(changed);
                    }
                    Map<String,Object> row = new LinkedHashMap<>();
                    row.put("color", color); row.put("seed", Long.toString(seed)); row.put("protocol", protocol);
                    row.put("mutated_current", mutated); row.put("offset", AbstractDungeon.cardBlizzRandomizer);
                    List<String> ids = new ArrayList<>();
                    for (AbstractCard value : cards) ids.add(value.cardID);
                    row.put("cards", ids);
                    Map<String,Object> states = new LinkedHashMap<>(), calls = new LinkedHashMap<>();
                    String[] names = {"card", "card_random", "neow", "misc"};
                    Trace[] rngs = {cardRng, randomRng, neowRng, miscRng};
                    for (int i = 0; i < names.length; i++) {
                        states.put(names[i], RewardReference.state(rngs[i]));
                        calls.put(names[i], rngs[i].calls);
                    }
                    row.put("states", states); row.put("calls", calls); output.add(row);
                }
            }
        }
        Files.write(Paths.get(args[2]), new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Special selection reference cases " + output.size());
    }
}

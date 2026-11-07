// Original JAR pool initialization/draws with prepared relic metadata/gates.
// Potion cases execute original PotionHelper and actual potion constructors.
import com.megacrit.cardcrawl.characters.AbstractPlayer;
import com.megacrit.cardcrawl.core.CardCrawlGame;
import com.megacrit.cardcrawl.dungeons.*;
import com.megacrit.cardcrawl.helpers.*;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.potions.AbstractPotion;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.unlock.UnlockTracker;
import com.google.gson.*;
import java.util.*;
import java.nio.file.*;
import java.lang.reflect.*;

public class ContentPoolReference {
    static final String[] TIERS = {"COMMON","UNCOMMON","RARE","SHOP","BOSS"};
    static Set<String> blocked = new HashSet<>();
    static Method initialize;
    static Object dungeon;

    static class Trace extends RewardReference.Trace {
        Trace(long seed) { super(seed); }
        public long randomLong() {
            long result = super.randomLong();
            calls.add(Arrays.asList("long", Long.toString(result)));
            return result;
        }
        public int random(int start, int end) {
            int result = super.random(start,end);
            calls.add(Arrays.asList("int_range", start, end, result));
            return result;
        }
    }

    static class MetaRelic extends AbstractRelic {
        private MetaRelic() { super("prepared", "prepared.png", RelicTier.COMMON, LandingSound.CLINK); }
        public String getUpdatedDescription() { return "prepared"; }
        public boolean canSpawn() { return !blocked.contains(relicId); }
        public AbstractRelic makeCopy() { return this; }
    }

    static AbstractRelic relic(String id, String tier) throws Exception {
        MetaRelic result = (MetaRelic)RewardReference.u.allocateInstance(MetaRelic.class);
        Field identity = AbstractRelic.class.getField("relicId");
        identity.setAccessible(true);
        identity.set(result,id);
        result.tier = AbstractRelic.RelicTier.valueOf(tier);
        return result;
    }

    @SuppressWarnings("unchecked")
    static Map<String,AbstractRelic> relicMap(String name) throws Exception {
        Field field = RelicLibrary.class.getDeclaredField(name);
        field.setAccessible(true);
        return (Map<String,AbstractRelic>)field.get(null);
    }

    @SuppressWarnings("unchecked")
    static ArrayList<String> pool(String tier) throws Exception {
        String name = tier.toLowerCase()+"RelicPool";
        return (ArrayList<String>)AbstractDungeon.class.getField(name).get(null);
    }

    static Map<String,Object> poolState() throws Exception {
        Map<String,Object> result = new LinkedHashMap<>();
        for (String tier:TIERS) result.put(tier, new ArrayList<>(pool(tier)));
        return result;
    }

    static Trace initializePools(long seed, AbstractPlayer.PlayerClass role) throws Exception {
        AbstractDungeon.player.chosenClass = role;
        AbstractDungeon.player.relics.clear();
        AbstractDungeon.floorNum = 0;
        Trace rng = new Trace(seed);
        AbstractDungeon.relicRng = rng;
        initialize.invoke(dungeon);
        return rng;
    }

    static void setup(JsonArray catalog) throws Exception {
        RewardReference.setup();
        Field potions = LocalizedStrings.class.getDeclaredField("potions");
        potions.setAccessible(true);
        potions.set(null, new HashMap<String,PotionStrings>() {
            public boolean containsKey(Object key) { return true; }
            public PotionStrings get(Object key) {
                PotionStrings value = new PotionStrings();
                value.NAME = key.toString();
                value.DESCRIPTIONS = new String[100];
                Arrays.fill(value.DESCRIPTIONS, "prepared");
                return value;
            }
        });
        Field keywords = LocalizedStrings.class.getDeclaredField("keywords");
        keywords.setAccessible(true);
        keywords.set(null,new HashMap<String,KeywordStrings>() {
            public KeywordStrings get(Object key) {
                KeywordStrings value = new KeywordStrings();
                value.TEXT = new String[]{"prepared"};
                for (Field field:KeywordStrings.class.getDeclaredFields()) {
                    if (field.getType()==Keyword.class) {
                        Keyword keyword = new Keyword();
                        keyword.NAMES = new String[]{"prepared"};
                        keyword.DESCRIPTION = "prepared";
                        try { field.set(value,keyword); } catch (Exception error) { throw new RuntimeException(error); }
                    }
                }
                return value;
            }
        });
        for (String name:new String[]{"sharedRelics","redRelics","greenRelics","blueRelics","purpleRelics"}) relicMap(name).clear();
        Map<String,String> names = new HashMap<>();
        names.put("any","sharedRelics"); names.put("ironclad","redRelics"); names.put("silent","greenRelics");
        names.put("defect","blueRelics"); names.put("watcher","purpleRelics");
        for (JsonElement entry:catalog) {
            JsonObject row = entry.getAsJsonObject();
            String id = row.get("id").getAsString();
            relicMap(names.get(row.get("namespace").getAsString())).put(id, relic(id,row.get("tier").getAsString()));
        }
        // Prepared fallback metadata avoids loading relic artwork during gate checks.
        relicMap("sharedRelics").put("Circlet", relic("Circlet","SPECIAL"));
        relicMap("sharedRelics").put("Red Circlet", relic("Red Circlet","SPECIAL"));
        UnlockTracker.lockedRelics.clear();
        dungeon = RewardReference.u.allocateInstance(Exordium.class);
        initialize = AbstractDungeon.class.getDeclaredMethod("initializeRelicList");
        initialize.setAccessible(true);
    }

    public static void main(String[] args) throws Exception {
        JsonObject source = new JsonParser().parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject();
        setup(source.getAsJsonArray("rows"));
        List<Object> output = new ArrayList<>();
        String[] roleNames = {"ironclad","silent","defect","watcher"};
        AbstractPlayer.PlayerClass[] roles = {AbstractPlayer.PlayerClass.IRONCLAD,AbstractPlayer.PlayerClass.THE_SILENT,AbstractPlayer.PlayerClass.DEFECT,AbstractPlayer.PlayerClass.WATCHER};
        for (int roleIndex=0;roleIndex<roles.length;roleIndex++) {
            for (long seed:new long[]{0,1,42,-1,20261029,20261107}) {
                Trace initialized = initializePools(seed,roles[roleIndex]);
                Map<String,Object> init = new LinkedHashMap<>();
                init.put("kind","initialize"); init.put("role",roleNames[roleIndex]); init.put("seed",Long.toString(seed));
                init.put("pools",poolState()); init.put("calls",initialized.calls); init.put("state",RewardReference.state(initialized));
                output.add(init);
                for (String tier:TIERS) for (boolean end:new boolean[]{false,true}) for (String scenario:new String[]{"plain","reject","tier_empty","all_empty"}) {
                    blocked.clear();
                    Trace rng = initializePools(seed,roles[roleIndex]);
                    if (scenario.equals("reject") && !pool(tier).isEmpty()) blocked.add(pool(tier).get(end && !tier.equals("BOSS")?pool(tier).size()-1:0));
                    if (scenario.equals("tier_empty")) pool(tier).clear();
                    if (scenario.equals("all_empty")) for (String value:TIERS) pool(value).clear();
                    Map<String,Object> row = new LinkedHashMap<>();
                    row.put("kind","relic_draw"); row.put("role",roleNames[roleIndex]); row.put("seed",Long.toString(seed));
                    row.put("tier",tier); row.put("from_end",end); row.put("scenario",scenario);
                    row.put("blocked",new ArrayList<>(blocked)); row.put("before",poolState());
                    List<String> results = new ArrayList<>();
                    for (int i=0;i<3;i++) results.add(end?AbstractDungeon.returnEndRandomRelicKey(AbstractRelic.RelicTier.valueOf(tier)):AbstractDungeon.returnRandomRelicKey(AbstractRelic.RelicTier.valueOf(tier)));
                    row.put("results",results); row.put("after",poolState()); row.put("calls",rng.calls); row.put("state",RewardReference.state(rng));
                    output.add(row);
                }
                PotionHelper.initialize(roles[roleIndex]);
                for (String mode:new String[]{"uniform","weighted","COMMON","UNCOMMON","RARE","limited_COMMON","limited_UNCOMMON","limited_RARE"}) {
                    Trace rng = new Trace(seed);
                    AbstractDungeon.potionRng = rng;
                    List<String> results = new ArrayList<>();
                    for (int i=0;i<5;i++) {
                        AbstractPotion potion;
                        if (mode.equals("uniform")) potion=PotionHelper.getRandomPotion();
                        else if (mode.equals("weighted")) potion=AbstractDungeon.returnRandomPotion(false);
                        else potion=AbstractDungeon.returnRandomPotion(AbstractPotion.PotionRarity.valueOf(mode.replace("limited_","")),mode.startsWith("limited_"));
                        results.add(potion.ID);
                    }
                    Map<String,Object> row = new LinkedHashMap<>();
                    row.put("kind","potion_draw"); row.put("role",roleNames[roleIndex]); row.put("seed",Long.toString(seed));
                    row.put("mode",mode); row.put("results",results); row.put("calls",rng.calls); row.put("state",RewardReference.state(rng));
                    output.add(row);
                }
            }
        }
        Files.write(Paths.get(args[1]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Content pool reference cases "+output.size());
    }
}

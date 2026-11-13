// Actual JAR base-price methods and setPrice, with source-derived initial formulas.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.potions.*;
import com.megacrit.cardcrawl.relics.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.shop.ShopScreen;
import com.badlogic.gdx.math.MathUtils;
import com.google.gson.*;
import com.megacrit.cardcrawl.localization.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

public class ShopPriceReference {
    static class Trace extends RewardReference.Trace {
        Float quantile;
        Trace(long seed) { super(seed); }
        public float random(float start,float end) {
            float value = quantile==null?super.random(start,end):start+quantile*(end-start);
            calls.add(Arrays.asList("float_range",(double)start,(double)end,(double)value));
            return value;
        }
    }
    static int initial(String kind,String tier,Trace rng) throws Exception {
        if (kind.equals("colored") || kind.equals("colorless")) {
            float value=AbstractCard.getPrice(AbstractCard.CardRarity.valueOf(tier))*rng.random(0.9f,1.1f);
            if (kind.equals("colorless")) value*=1.2f;
            return (int)value;
        }
        int base;
        if (kind.equals("relic")) base=ContentPoolReference.relic("prepared",tier).getPrice();
        else {
            AbstractPotion potion=(AbstractPotion)RewardReference.u.allocateInstance(FirePotion.class);
            potion.rarity=AbstractPotion.PotionRarity.valueOf(tier);
            base=potion.getPrice();
        }
        return MathUtils.round(base*rng.random(0.95f,1.05f));
    }
    public static void main(String[] args) throws Exception {
        RewardReference.setup();
        Field potions=LocalizedStrings.class.getDeclaredField("potions");
        potions.setAccessible(true);
        potions.set(null,new HashMap<String,PotionStrings>() {
            public boolean containsKey(Object key) { return true; }
            public PotionStrings get(Object key) {
                PotionStrings value=new PotionStrings();value.NAME=key.toString();
                value.DESCRIPTIONS=new String[]{"prepared"};return value;
            }
        });
        Method setPrice=ShopScreen.class.getDeclaredMethod("setPrice",AbstractCard.class);
        setPrice.setAccessible(true);
        Object screen=RewardReference.u.allocateInstance(ShopScreen.class);
        List<Object> out=new ArrayList<>();
        for (String kind:new String[]{"colored","colorless","relic","potion"}) {
            String[] tiers=kind.equals("colorless")?new String[]{"UNCOMMON","RARE"}:kind.equals("relic")?new String[]{"COMMON","UNCOMMON","RARE","SHOP","SPECIAL"}:new String[]{"COMMON","UNCOMMON","RARE"};
            for (String tier:tiers) {
                for (long seed:new long[]{0,1,42,-1,20261109}) {
                    Trace rng=new Trace(seed);List<Integer> prices=new ArrayList<>();
                    for (int i=0;i<20;i++) prices.add(initial(kind,tier,rng));
                    Map<String,Object> row=new LinkedHashMap<>();row.put("mode","seeded");row.put("kind",kind);row.put("tier",tier);row.put("seed",Long.toString(seed));row.put("prices",prices);row.put("calls",rng.calls);row.put("state",RewardReference.state(rng));out.add(row);
                }
                Trace rng=new Trace(0);List<Integer> prices=new ArrayList<>();List<Double> quantiles=new ArrayList<>();
                for (int i=0;i<1000;i++) {
                    rng.quantile=(i+0.5f)/1000f;quantiles.add((double)rng.quantile);prices.add(initial(kind,tier,rng));
                }
                for (float value:new float[]{0f,0.5f,Math.nextDown(1f)}) {
                    rng.quantile=value;quantiles.add((double)value);prices.add(initial(kind,tier,rng));
                }
                Map<String,Object> row=new LinkedHashMap<>();row.put("mode","grid");row.put("kind",kind);row.put("tier",tier);row.put("quantiles",quantiles);row.put("prices",prices);out.add(row);
                if (!kind.equals("colored") && !kind.equals("colorless")) continue;
                for (boolean courier:new boolean[]{false,true}) for (boolean membership:new boolean[]{false,true}) for (long seed:new long[]{0,1,42,-1,20261109}) {
                    AbstractDungeon.player.relics.clear();
                    if (courier) AbstractDungeon.player.relics.add(ContentPoolReference.relic("The Courier","SHOP"));
                    if (membership) AbstractDungeon.player.relics.add(ContentPoolReference.relic("Membership Card","SHOP"));
                    Trace trace=new Trace(seed);AbstractDungeon.merchantRng=trace;List<Integer> result=new ArrayList<>();
                    for (int i=0;i<20;i++) {
                        AbstractCard c=RewardReference.card("prepared",AbstractCard.CardRarity.valueOf(tier));
                        c.color=kind.equals("colorless")?AbstractCard.CardColor.COLORLESS:AbstractCard.CardColor.RED;
                        setPrice.invoke(screen,c);result.add(c.price);
                    }
                    Map<String,Object> item=new LinkedHashMap<>();item.put("mode","restock");item.put("kind",kind);item.put("tier",tier);item.put("courier",courier);item.put("membership",membership);item.put("seed",Long.toString(seed));item.put("prices",result);item.put("calls",trace.calls);item.put("state",RewardReference.state(trace));out.add(item);
                }
            }
        }
        Files.write(Paths.get(args[0]),new Gson().toJson(out).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Price reference rows "+out.size());
    }
}

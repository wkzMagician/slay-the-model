// Actual original applyDiscount/getNewPrice with prepared inventories.
// Post-purge refresh is reconstructed from the fixed purgeCard price branch.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.shop.*;
import com.badlogic.gdx.math.MathUtils;
import com.google.gson.*;
import java.nio.file.*;
import java.lang.reflect.*;
import java.util.*;

public class ShopSettlementReference {
    static void set(Object target,Class<?> owner,String name,Object value) throws Exception {
        Field f=owner.getDeclaredField(name);f.setAccessible(true);f.set(target,value);
    }
    static int cost() throws Exception {
        Field f=ShopScreen.class.getDeclaredField("actualPurgeCost");f.setAccessible(true);return f.getInt(null);
    }
    static ShopScreen screen(AbstractCard card,StoreRelic relic,StorePotion potion) throws Exception {
        ShopScreen screen=(ShopScreen)RewardReference.u.allocateInstance(ShopScreen.class);
        set(screen,ShopScreen.class,"coloredCards",new ArrayList<>(Arrays.asList(card)));
        set(screen,ShopScreen.class,"colorlessCards",new ArrayList<AbstractCard>());
        set(screen,ShopScreen.class,"relics",new ArrayList<>(Arrays.asList(relic)));
        set(screen,ShopScreen.class,"potions",new ArrayList<>(Arrays.asList(potion)));
        return screen;
    }
    static void held(boolean courier,boolean membership,boolean mask) throws Exception {
        AbstractDungeon.player.relics.clear();
        if(courier)AbstractDungeon.player.relics.add(ContentPoolReference.relic("The Courier","UNCOMMON"));
        if(membership)AbstractDungeon.player.relics.add(ContentPoolReference.relic("Membership Card","SHOP"));
        if(mask)AbstractDungeon.player.relics.add(ContentPoolReference.relic("Smiling Mask","COMMON"));
    }
    public static void main(String[] args) throws Exception {
        RewardReference.setup();List<Object> output=new ArrayList<>();
        int[] bases={1,45,51,75,100,101,150,999};
        for(int asc:new int[]{0,15,16,20})for(int base:bases)for(boolean sale:new boolean[]{false,true})for(boolean courier:new boolean[]{false,true})for(boolean membership:new boolean[]{false,true})for(boolean mask:new boolean[]{false,true}) {
            held(courier,membership,mask);
            AbstractCard card=RewardReference.card("prepared",AbstractCard.CardRarity.COMMON);card.price=sale?base/2:base;
            StoreRelic relic=(StoreRelic)RewardReference.u.allocateInstance(StoreRelic.class);relic.price=base;
            StorePotion potion=(StorePotion)RewardReference.u.allocateInstance(StorePotion.class);potion.price=base;
            ShopScreen screen=screen(card,relic,potion);
            set(null,ShopScreen.class,"purgeCost",75);set(null,ShopScreen.class,"actualPurgeCost",75);
            if(asc>=16)screen.applyDiscount(1.1f,false);
            if(courier)screen.applyDiscount(0.8f,true);
            if(membership)screen.applyDiscount(0.5f,true);
            if(mask)set(null,ShopScreen.class,"actualPurgeCost",50);
            Map<String,Object> row=new LinkedHashMap<>();row.put("kind","initial");row.put("ascension",asc);row.put("base",base);row.put("sale",sale);row.put("courier",courier);row.put("membership",membership);row.put("mask",mask);
            row.put("card",card.price);row.put("relic",relic.price);row.put("potion",potion.price);row.put("removal",cost());
            screen.applyDiscount(0.5f,true);
            row.put("dynamic_card",card.price);row.put("dynamic_relic",relic.price);row.put("dynamic_potion",potion.price);row.put("dynamic_removal",cost());output.add(row);
        }
        for(int base:new int[]{75,100,125,150,175})for(boolean courier:new boolean[]{false,true})for(boolean membership:new boolean[]{false,true})for(boolean mask:new boolean[]{false,true}) {
            held(courier,membership,mask);
            AbstractCard card=RewardReference.card("prepared",AbstractCard.CardRarity.COMMON);StoreRelic relic=(StoreRelic)RewardReference.u.allocateInstance(StoreRelic.class);StorePotion potion=(StorePotion)RewardReference.u.allocateInstance(StorePotion.class);
            ShopScreen screen=screen(card,relic,potion);set(null,ShopScreen.class,"purgeCost",base);set(null,ShopScreen.class,"actualPurgeCost",base);
            if(courier)screen.applyDiscount(0.8f,true);if(membership)screen.applyDiscount(0.5f,true);if(mask)set(null,ShopScreen.class,"actualPurgeCost",50);
            int initial=cost();float value=base;if(courier)value*=0.8f;if(membership)value*=0.5f;
            Map<String,Object> row=new LinkedHashMap<>();row.put("kind","removal");row.put("base",base);row.put("courier",courier);row.put("membership",membership);row.put("mask",mask);row.put("initial",initial);row.put("after_removal",mask?50:MathUtils.round(value));output.add(row);
        }
        for(int base:new int[]{75,101,150,250,300,400})for(boolean courier:new boolean[]{false,true})for(boolean membership:new boolean[]{false,true})for(long seed:new long[]{0,1,42,-1}) {
            held(courier,membership,false);
            ShopScreen screen=(ShopScreen)RewardReference.u.allocateInstance(ShopScreen.class);
            ShopPriceReference.Trace rng=new ShopPriceReference.Trace(seed);AbstractDungeon.merchantRng=rng;
            StoreRelic relic=(StoreRelic)RewardReference.u.allocateInstance(StoreRelic.class);relic.price=base;screen.getNewPrice(relic);
            StorePotion potion=(StorePotion)RewardReference.u.allocateInstance(StorePotion.class);potion.price=base;screen.getNewPrice(potion);
            Map<String,Object> row=new LinkedHashMap<>();row.put("kind","restock");row.put("base",base);row.put("seed",Long.toString(seed));row.put("courier",courier);row.put("membership",membership);row.put("relic",relic.price);row.put("potion",potion.price);row.put("calls",rng.calls);row.put("state",RewardReference.state(rng));output.add(row);
        }
        Files.write(Paths.get(args[0]),new Gson().toJson(output).getBytes(java.nio.charset.StandardCharsets.UTF_8));
        System.out.println("Settlement rows "+output.size());
    }
}

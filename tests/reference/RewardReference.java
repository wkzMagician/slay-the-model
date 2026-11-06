// Executes original JAR reward logic with explicitly prepared metadata cards.
// Card constructors/effects, localization and gameplay are outside this oracle.
import com.megacrit.cardcrawl.cards.*;
import com.megacrit.cardcrawl.characters.*;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.rooms.*;
import com.megacrit.cardcrawl.random.Random;
import com.megacrit.cardcrawl.localization.*;
import com.megacrit.cardcrawl.core.CardCrawlGame;
import com.google.gson.*;
import java.util.*;
import java.nio.file.*;

public class RewardReference {
 static sun.misc.Unsafe u;
 static class Mode extends com.badlogic.gdx.Graphics.DisplayMode {Mode() {super(1920,1080,60,32);}}
 static class MetaCard extends AbstractCard {
  private MetaCard() {super("prepared","prepared",null,0,"",CardType.ATTACK,CardColor.RED,CardRarity.COMMON,CardTarget.NONE);}
  public void use(AbstractPlayer p,AbstractMonster m) {}
  public boolean canUpgrade() {return !upgraded;}
  public void upgrade() {upgraded=true;timesUpgraded++;}
  public AbstractCard makeCopy() {return card(cardID,rarity);}
 }
 static MetaCard card(String id,AbstractCard.CardRarity rarity) {
  try {MetaCard c=(MetaCard)u.allocateInstance(MetaCard.class);c.cardID=id;c.rarity=rarity;c.type=AbstractCard.CardType.ATTACK;return c;}
  catch(Exception e) {throw new RuntimeException(e);}
 }
 static class Trace extends Random {
  List<Object> calls=new ArrayList<>();
  Trace(long seed) {super(seed);}
  public int random(int bound) {int v=super.random(bound);calls.add(Arrays.asList("int",bound,v));return v;}
  public boolean randomBoolean(float chance) {boolean v=super.randomBoolean(chance);calls.add(Arrays.asList("boolean",chance,v));return v;}
 }
 static void setup() throws Exception {
  java.lang.reflect.Field uf=sun.misc.Unsafe.class.getDeclaredField("theUnsafe");uf.setAccessible(true);u=(sun.misc.Unsafe)uf.get(null);
  com.badlogic.gdx.Gdx.files=(com.badlogic.gdx.Files)java.lang.reflect.Proxy.newProxyInstance(RewardReference.class.getClassLoader(),new Class[]{com.badlogic.gdx.Files.class},(p,m,a)-> {
   if(m.getReturnType()==com.badlogic.gdx.files.FileHandle.class)return new com.badlogic.gdx.files.FileHandle(".bugs/fixes/p4-card-rewards-2026-11-05/missing-resources/"+a[0]);
   if(m.getReturnType()==boolean.class)return false;return "";
  });
  LocalizedStrings pack=(LocalizedStrings)u.allocateInstance(LocalizedStrings.class);
  java.lang.reflect.Field ui=LocalizedStrings.class.getDeclaredField("ui");ui.setAccessible(true);
  ui.set(null,new HashMap<String,UIStrings>() {public UIStrings get(Object key) {UIStrings v=new UIStrings();v.TEXT=new String[100];Arrays.fill(v.TEXT,"prepared");return v;}});
  java.lang.reflect.Field chars=LocalizedStrings.class.getDeclaredField("characters");chars.setAccessible(true);
  chars.set(null,new HashMap<String,CharacterStrings>() {public CharacterStrings get(Object key) {CharacterStrings v=new CharacterStrings();v.NAMES=new String[]{"prepared"};v.TEXT=new String[100];return v;}});
  CardCrawlGame.languagePack=pack;
  com.badlogic.gdx.graphics.Texture texture=(com.badlogic.gdx.graphics.Texture)u.allocateInstance(com.badlogic.gdx.graphics.Texture.class);
  java.lang.reflect.Field data=com.badlogic.gdx.graphics.Texture.class.getDeclaredField("data");data.setAccessible(true);
  data.set(texture,java.lang.reflect.Proxy.newProxyInstance(RewardReference.class.getClassLoader(),new Class[]{com.badlogic.gdx.graphics.TextureData.class},(p,m,a)-> {if(m.getReturnType()==int.class)return 64;if(m.getReturnType()==boolean.class)return false;return null;}));
  for(java.lang.reflect.Field f:com.megacrit.cardcrawl.helpers.ImageMaster.class.getDeclaredFields())if(f.getType()==com.badlogic.gdx.graphics.Texture.class) {f.setAccessible(true);if(f.get(null)==null)f.set(null,texture);}
  com.megacrit.cardcrawl.core.Settings.language=com.megacrit.cardcrawl.core.Settings.GameLanguage.ENG;
  com.badlogic.gdx.Gdx.graphics=(com.badlogic.gdx.Graphics)java.lang.reflect.Proxy.newProxyInstance(RewardReference.class.getClassLoader(),new Class[]{com.badlogic.gdx.Graphics.class},(p,m,a)-> {
   if(m.getReturnType()==com.badlogic.gdx.Graphics.DisplayMode.class)return new Mode();
   if(m.getReturnType()==com.badlogic.gdx.Graphics.DisplayMode[].class)return new com.badlogic.gdx.Graphics.DisplayMode[]{new Mode()};
   if(m.getReturnType()==int.class)return 60;if(m.getReturnType()==boolean.class)return false;return null;
  });
  for(java.lang.reflect.Field f:com.megacrit.cardcrawl.core.Settings.class.getDeclaredFields())if(f.getType()==com.megacrit.cardcrawl.helpers.Prefs.class) {f.setAccessible(true);f.set(null,new com.megacrit.cardcrawl.helpers.Prefs());}
  for(java.lang.reflect.Field f:com.megacrit.cardcrawl.unlock.UnlockTracker.class.getDeclaredFields())if(f.getType()==com.megacrit.cardcrawl.helpers.Prefs.class) {f.setAccessible(true);f.set(null,new com.megacrit.cardcrawl.helpers.Prefs());}
  com.badlogic.gdx.graphics.g2d.BitmapFont font=new com.badlogic.gdx.graphics.g2d.BitmapFont(new com.badlogic.gdx.graphics.g2d.BitmapFont.BitmapFontData(),new com.badlogic.gdx.graphics.g2d.TextureRegion(),false);
  for(java.lang.reflect.Field f:com.megacrit.cardcrawl.helpers.FontHelper.class.getDeclaredFields())if(f.getType()==com.badlogic.gdx.graphics.g2d.BitmapFont.class) {f.setAccessible(true);f.set(null,font);}
  java.lang.reflect.Field tutorials=LocalizedStrings.class.getDeclaredField("tutorials");tutorials.setAccessible(true);tutorials.set(null,new HashMap<String,TutorialStrings>());
  AbstractDungeon.player=(Ironclad)u.allocateInstance(Ironclad.class);AbstractDungeon.player.relics=new ArrayList<>();
  AbstractDungeon.cardBlizzStartOffset=5;AbstractDungeon.cardBlizzGrowth=1;AbstractDungeon.cardBlizzMaxOffset=-40;
 }
 static Map<String,Object> state(Trace r) {Map<String,Object> s=new LinkedHashMap<>();s.put("state0",Long.toString(r.random.getState(0)));s.put("state1",Long.toString(r.random.getState(1)));s.put("counter",r.counter);return s;}
 public static void main(String[] args) throws Exception {
  setup();JsonArray pools=new JsonParser().parse(new String(Files.readAllBytes(Paths.get(args[0])),"UTF-8")).getAsJsonObject().getAsJsonArray("pools");
  List<Object> out=new ArrayList<>();
  for(String color:new String[]{"RED","GREEN","BLUE","PURPLE"}) {
   for(JsonElement entry:pools) {JsonObject p=entry.getAsJsonObject();if(!color.equals(p.get("color").getAsString()))continue;
    AbstractCard.CardRarity tier=AbstractCard.CardRarity.valueOf(p.get("rarity").getAsString());CardGroup group=new CardGroup(CardGroup.CardGroupType.CARD_POOL);
    for(JsonElement id:p.getAsJsonArray("initialized"))group.addToTop(card(id.getAsString(),tier));
    switch(tier) {case COMMON:AbstractDungeon.commonCardPool=group;break;case UNCOMMON:AbstractDungeon.uncommonCardPool=group;break;case RARE:AbstractDungeon.rareCardPool=group;break;default:throw new RuntimeException();}
   }
   for(long seed:new long[]{0,1,42,-1})for(int offset:new int[]{5,0,-40})for(int act=1;act<=3;act++)for(int asc:new int[]{0,12})for(boolean elite:new boolean[]{false,true}) {
    Trace rng=new Trace(seed);AbstractDungeon.cardRng=rng;AbstractDungeon.cardBlizzRandomizer=offset;
    java.lang.reflect.Field chance=AbstractDungeon.class.getDeclaredField("cardUpgradedChance");chance.setAccessible(true);chance.setFloat(null,(act==1?0f:act==2?.25f:.5f)/(asc>=12?2:1));
    MapRoomNode node=new MapRoomNode(0,0);node.setRoom(elite?new MonsterRoomElite():new MonsterRoom());AbstractDungeon.currMapNode=node;
    Map<String,Object> row=new LinkedHashMap<>();row.put("color",color);row.put("seed",Long.toString(seed));row.put("offset",offset);row.put("act",act);row.put("ascension",asc);row.put("encounter",elite?"elite":"normal");
    List<Object> rewards=new ArrayList<>();for(AbstractCard c:AbstractDungeon.getRewardCards())rewards.add(Arrays.asList(c.cardID,c.timesUpgraded));
    row.put("cards",rewards);row.put("calls",rng.calls);row.put("after_offset",AbstractDungeon.cardBlizzRandomizer);row.put("state",state(rng));out.add(row);
   }
  }
  Files.write(Paths.get(args[1]),new Gson().toJson(out).getBytes(java.nio.charset.StandardCharsets.UTF_8));System.out.println("Actual JAR getRewardCards cases: "+out.size());
 }
}

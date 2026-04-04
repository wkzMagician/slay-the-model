"""
All game power definitions.
Powers are temporary or permanent combat effects.
"""
from powers.definitions.strength import StrengthPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from powers.definitions.strength_down import StrengthDownPower
from powers.definitions.confused import ConfusedPower
from powers.definitions.no_block import NoBlockPower
from powers.definitions.artifact import ArtifactPower
from powers.definitions.intangible import IntangiblePower
from powers.definitions.frail import FrailPower
from powers.definitions.magnetism import MagnetismPower
from powers.definitions.mayhem import MayhemPower
from powers.definitions.panache import PanachePower
from powers.definitions.sadistic_nature import SadisticNaturePower
from powers.definitions.the_bomb import TheBombPower
from powers.definitions.thorns import ThornsPower
from powers.definitions.poison import PoisonPower
from powers.definitions.plated_armor import PlatedArmorPower
from powers.definitions.dexterity import DexterityPower
from powers.definitions.ritual import RitualPower
from powers.definitions.duplication import DuplicationPower
from powers.definitions.regeneration import RegenerationPower
from powers.definitions.pen_nib import PenNibPower
from powers.definitions.barricade import BarricadePower
from powers.definitions.berserk import BerserkPower
from powers.definitions.brutality import BrutalityPower
from powers.definitions.combust import CombustPower
from powers.definitions.corruption import CorruptionPower
from powers.definitions.dark_embrace import DarkEmbracePower
from powers.definitions.demon_form import DemonFormPower
from powers.definitions.double_tap import DoubleTapPower
from powers.definitions.evolve import EvolvePower
from powers.definitions.fire_breathing import FireBreathing
from powers.definitions.flame_barrier import FlameBarrierPower
from powers.definitions.feel_no_pain import FeelNoPainPower
from powers.definitions.juggernaut import JuggernautPower
from powers.definitions.metallicize import MetallicizePower
from powers.definitions.rage import RagePower
from powers.definitions.no_draw import NoDrawPower
from powers.definitions.battle_trance_draw_power import BattleTranceDrawPower
from powers.definitions.buffer import BufferPower
from powers.definitions.rupture import RupturePower
from powers.definitions.enrage import EnragePower
from powers.definitions.entangled import EntangledPower
from powers.definitions.curiosity import CuriosityPower
from powers.definitions.draw_reduction import DrawReductionPower
from powers.definitions.constricted import ConstrictedPower
from powers.definitions.flying import FlyingPower
from powers.definitions.hex import HexPower
from powers.definitions.focus import FocusPower
from powers.definitions.strength_up import StrengthUpPower
from powers.definitions.fading import FadingPower
from powers.definitions.shifting import ShiftingPower
from powers.definitions.beat_of_death import BeatOfDeathPower
from powers.definitions.painful_stabs import PainfulStabsPower
from powers.definitions.accuracy import AccuracyPower
from powers.definitions.infinite_blades import InfiniteBladesPower
from powers.definitions.noxious_fumes import NoxiousFumesPower
from powers.definitions.energized import EnergizedPower
from powers.definitions.draw_card_next_turn import DrawCardNextTurnPower
from powers.definitions.next_turn_block import NextTurnBlockPower
from powers.definitions.choke import ChokePower

__all__ = [
    "StrengthPower",
    "VulnerablePower",
    "WeakPower",
    "StrengthDownPower",
    "ConfusedPower",
    "NoBlockPower",
    "ArtifactPower",
    "IntangiblePower",
    "FrailPower",
    "MagnetismPower",
    "MayhemPower",
    "PanachePower",
    "SadisticNaturePower",
    "TheBombPower",
    "ThornsPower",
    "PoisonPower",
    "PlatedArmorPower",
    "DexterityPower",
    "RitualPower",
    "DuplicationPower",
    "RegenerationPower",
    "PenNibPower",
    "BarricadePower",
    "BerserkPower",
    "BrutalityPower",
    "CombustPower",
    "CorruptionPower",
    "DarkEmbracePower",
    "DemonFormPower",
    "DoubleTapPower",
    "EvolvePower",
    "FireBreathing",
    "FlameBarrierPower",
    "FeelNoPainPower",
    "JuggernautPower",
    "MetallicizePower",
    "RagePower",
    "NoDrawPower",
    "BattleTranceDrawPower",
    "BufferPower",
    "RupturePower",
    "EnragePower",
    "EntangledPower",
    "CuriosityPower",
    "DrawReductionPower",
    "ConstrictedPower",
    "StrengthUpPower",
    "FadingPower",
    "ShiftingPower",
    "BeatOfDeathPower",
    "PainfulStabsPower",
    "AccuracyPower",
    "InfiniteBladesPower",
    "NoxiousFumesPower",
    "EnergizedPower",
    "DrawCardNextTurnPower",
    "NextTurnBlockPower",
    "ChokePower",
    "FlyingPower",
    "FocusPower",
    "HexPower",
    "AfterImagePower",
    "EnvenomPower",
    "ThousandCutsPower",
    "BlurPower",
    "DexterityDownPower",
    "EscapePlanCheckPower",
    "PhantasmalKillerPower",
    "PhantasmalNextTurnPower",
    "BurstPower",
    "CorpseExplosionPower",
    "NightmarePower",
    "ToolsOfTheTradePower",
    "WellLaidPlansPower",
]
from powers.definitions.after_image import AfterImagePower
from powers.definitions.envenom import EnvenomPower
from powers.definitions.thousand_cuts import ThousandCutsPower

from powers.definitions.blur import BlurPower
from powers.definitions.dexterity_down import DexterityDownPower
from powers.definitions.escape_plan_check import EscapePlanCheckPower
from powers.definitions.phantasmal_killer import PhantasmalKillerPower
from powers.definitions.phantasmal_next_turn import PhantasmalNextTurnPower
from powers.definitions.burst import BurstPower
from powers.definitions.corpse_explosion import CorpseExplosionPower
from powers.definitions.nightmare import NightmarePower
from powers.definitions.tools_of_the_trade import ToolsOfTheTradePower
from powers.definitions.well_laid_plans import WellLaidPlansPower
from powers.definitions.lock_on import LockOnPower
from powers.definitions.electro import ElectroPower
from powers.definitions.loop import LoopPower
from powers.definitions.storm import StormPower
from powers.definitions.static_discharge import StaticDischargePower
from powers.definitions.heatsinks import HeatsinksPower
from powers.definitions.machine_learning import MachineLearningPower
from powers.definitions.hello_world import HelloWorldPower
from powers.definitions.creative_ai import CreativeAIPower
from powers.definitions.self_repair import SelfRepairPower
from powers.definitions.biased_cognition import BiasedCognitionPower
from powers.definitions.amplify import AmplifyPower
from powers.definitions.echo_form import EchoFormPower
from powers.definitions.battle_hymn import BattleHymnPower
from powers.definitions.blasphemer import BlasphemerPower
from powers.definitions.collect import CollectPower
from powers.definitions.deva import DevaPower
from powers.definitions.devotion import DevotionPower
from powers.definitions.establishment import EstablishmentPower
from powers.definitions.fasting import FastingPower
from powers.definitions.foresight import ForesightPower
from powers.definitions.like_water import LikeWaterPower
from powers.definitions.mantra import MantraPower
from powers.definitions.mark import MarkPower
from powers.definitions.master_reality import MasterRealityPower
from powers.definitions.mental_fortress import MentalFortressPower
from powers.definitions.nirvana import NirvanaPower
from powers.definitions.omega import OmegaPower
from powers.definitions.rushdown import RushdownPower
from powers.definitions.study import StudyPower
from powers.definitions.talk_to_the_hand import TalkToTheHandPower
from powers.definitions.temporary_dexterity import TemporaryDexterityPower
from powers.definitions.wave_of_the_hand import WaveOfTheHandPower
from powers.definitions.wreath_of_flame import WreathOfFlamePower

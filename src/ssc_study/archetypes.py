"""Question archetype classification and accuracy tracking.

Archetypes are conceptual clusters within each SSC CGL section
(e.g. "Number Systems" under Quant/DI, "Blood Relations" under Reasoning).
This module provides:

  - Rule-based archetype assignment from question text keywords.
  - Database persistence for archetypes and question→archetype mapping.
  - Accuracy probing: pick sample questions to estimate archetype mastery.
  - Weak-archetype detection for targeted practice recommendations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .db import Database
from .models import Question

# ── Archetype definitions ──────────────────────────────────────────────
# Each archetype has a name, section, and keyword patterns.
# Patterns are compiled once at module load.

@dataclass(frozen=True)
class ArchetypeDef:
    """Definition of a question archetype with matching keywords."""
    name: str
    section: str
    tier: str  # 'tier1' | 'tier2' | 'both'
    difficulty: str  # 'easy' | 'medium' | 'hard'
    keywords: tuple[str, ...]  # regex patterns (lowercase)


# fmt: off
ARCHETYPE_DEFS: list[ArchetypeDef] = [
    # ── Quant / DI ──────────────────────────────────────────────────
    ArchetypeDef("Number Systems", "Quant/DI", "both", "medium", (
        r"number\s*(system|theory)", r"divisibility", r"prime\b", r"hcf", r"lcm",
        r"unit\s*digit", r"remainder", r"factor", r"integer", r"real\s*number",
        r"rational", r"irrational", r"even\s*number", r"odd\s*number",
        r"consecutive\s*number", r"square\s*root", r"cube\s*root",
    )),
    ArchetypeDef("Algebra", "Quant/DI", "both", "medium", (
        r"algebra", r"equation", r"polynomial", r"quadratic", r"linear\s*equation",
        r"simultaneous", r"factorization", r"identity", r"binomial",
        r"inequality", r"exponent", r"surds?", r"indices?",
        r"if\s*.*=.*\s*then\b", r"find\s*the\s*value\s*of\b",
        r"x\s*\+\s*y", r"a\s*\+\s*b", r"simplify", r"evaluate",
    )),
    ArchetypeDef("Geometry", "Quant/DI", "both", "medium", (
        r"geometry", r"triangle", r"circle", r"angle", r"parallel\s*line",
        r"perpendicular", r"congruent", r"similar\s*triangle", r"pythagor",
        r"chord", r"tangent", r"secant", r"arc\b", r"sector", r"polygon",
        r"quadrilateral", r"rectangle", r"square\b", r"parallelogram",
        r"rhombus", r"trapezium", r"inscribed", r"circumscribed",
        r"circumference", r"diameter", r"radius", r"bisect",
    )),
    ArchetypeDef("Mensuration", "Quant/DI", "both", "medium", (
        r"mensuration", r"area\b", r"volume", r"surface\s*area",
        r"perimeter", r"cylinder", r"cone\b", r"sphere", r"hemisphere",
        r"cuboid", r"cube\b", r"prism", r"pyramid", r"frustum",
        r"length\b", r"breadth", r"height\b", r"radius", r"diameter",
        r"curved\s*surface", r"total\s*surface", r"cross.section",
        r"dimensions?\s*of", r"find\s*the\s*area",
    )),
    ArchetypeDef("Trigonometry", "Quant/DI", "both", "hard", (
        r"trigonometry", r"sin\b", r"cos\b", r"tan\b", r"cosec", r"sec\b", r"cot\b",
        r"angle\s*of\s*elevation", r"angle\s*of\s*depression",
        r"heights?\s*and\s*distances?", r"bearing",
        r"trigonometric", r"identity",
    )),
    ArchetypeDef("Data Interpretation", "Quant/DI", "both", "medium", (
        r"data\s*interpretation", r"table\s*show", r"bar\s*graph", r"pie\s*chart",
        r"line\s*graph", r"following\s*table", r"below\s*table",
        r"study\s*the\s*(table|chart|graph)", r"based\s*on\s*the\s*(table|graph)",
        r"di\b(?!.*quant)", r"tabular", r"chart\b", r"graph\b",
        r"following\s*figures?\s*show", r"number\s*of\s*students",
        r"production\s*of", r"expenditure", r"percentage\s*distribution",
    )),
    ArchetypeDef("Percentages & Ratios", "Quant/DI", "both", "easy", (
        r"percent", r"ratio", r"proportion", r"\d+\s*%", r"percentage",
        r"part\s*of\b", r"fraction", r"decimal",
        r"out\s*of\b", r"per\s*centum", r"as\s*a\s*percentage",
        r"what\s*percent", r"what\s*is\s*the\s*ratio",
        r"divide[sd]?\s*in\s*the\s*ratio",
    )),
    ArchetypeDef("Time & Work", "Quant/DI", "both", "medium", (
        r"time\s*and\s*work", r"work\b", r"days?\s*to\s*complete", r"efficiency",
        r"pipe[s]?", r"cistern", r"tank\b", r"fill[s]?\s*a\s*tank",
        r"can\s*do\s*a\s*work", r"A\s*and\s*B\s*together",
        r"alone\s*can\s*do", r"men\s*can\s*do", r"workers?",
        r"complete\s*(the\s*)?work", r"piece\s*of\s*work",
        r"work\s*efficiency",
    )),
    ArchetypeDef("Speed, Time & Distance", "Quant/DI", "both", "easy", (
        r"speed", r"distance", r"train\s*(cross|pass|length|speed)", r"boat",
        r"stream", r"upstream", r"downstream", r"average\s*speed",
        r"km/h", r"km\s*per\s*hour", r"m/s", r"meter\s*per\s*second",
        r"car\b.*travel", r"cycle\b", r"walking\s*speed",
        r"relative\s*speed", r"time\s*taken",
    )),
    ArchetypeDef("Averages & Mixtures", "Quant/DI", "both", "easy", (
        r"average", r"mean\b", r"mixture", r"alligation", r"weighted\s*average",
        r"median", r"mode\b", r"combined\s*average",
        r"average\s*age", r"average\s*weight", r"average\s*marks",
        r"average\s*of", r"mean\s*of",
        r"mixed", r"in\s*the\s*ratio.*mixed",
    )),
    ArchetypeDef("Interest", "Quant/DI", "both", "medium", (
        r"interest", r"compound\s*interest", r"simple\s*interest",
        r"ci\b", r"si\b", r"principal", r"amount\b", r"rate\s*of\s*interest",
        r"sum\s*of\s*money.*interest", r"compounded\s*annually",
        r"compounded\s*half.yearly",
    )),
    ArchetypeDef("Profit & Loss", "Quant/DI", "both", "easy", (
        r"profit", r"loss\b", r"discount", r"cost\s*price", r"selling\s*price",
        r"marked\s*price", r"market\s*price", r"overhead", r"gain\b",
        r"profit\s*percent", r"loss\s*percent", r"sp\b", r"cp\b",
        r"sold\s*at", r"bought\s*at", r"article.*cost",
    )),

    # ── Reasoning ───────────────────────────────────────────────────
    ArchetypeDef("Analogies", "Reasoning", "both", "easy", (
        r"analogy", r"is\s*to\b", r"as\s*is\s*to", r"related\s*to",
        r":\s*\w+\s*::", r"similar\s*relationship",
        r"find\s*the\s*analogy", r"analogous",
    )),
    ArchetypeDef("Coding-Decoding", "Reasoning", "both", "medium", (
        r"coding", r"decoding", r"code\b", r"coded\s*as", r"coded\s*language",
        r"in\s*a\s*certain\s*code", r"code\s*for", r"decipher",
        r"is\s*coded\s*as", r"stands\s*for",
    )),
    ArchetypeDef("Blood Relations", "Reasoning", "both", "medium", (
        r"blood\s*relation", r"family\s*tree", r"brother", r"sister",
        r"father", r"mother", r"uncle", r"aunt", r"nephew", r"niece",
        r"grandfather", r"grandmother", r"cousin", r"son\b", r"daughter",
        r"husband", r"wife\b", r"mother.in.law", r"father.in.law",
        r"how\s+is\s+\w+\s+related\s+to",
        r"family\s*member", r"paternal", r"maternal",
    )),
    ArchetypeDef("Syllogisms", "Reasoning", "both", "hard", (
        r"syllogism", r"statement", r"conclusion", r"all\s+\w+\s+are",
        r"some\s+\w+\s+are", r"no\s+\w+\s+is", r"some\s+not",
        r"only\s+a\s+few", r"follows?", r"conclusions?:",
        r"statements?:", r"which\s*of\s*the\s*following\s*conclusions?",
    )),
    ArchetypeDef("Seating Arrangement", "Reasoning", "both", "hard", (
        r"seating\s*arrangement", r"sitting\s*in\s*a\s*row", r"sitting\s*around",
        r"circular\s*table", r"linear\s*arrangement",
        r"arranged\s*in\s*a\s*row", r"sitting\s*in\s*a\s*circle",
        r"facing\s*(north|south|east|west)", r"bench\b",
        r"row\b.*sitting", r"sit\s*between",
    )),
    ArchetypeDef("Puzzles", "Reasoning", "both", "hard", (
        r"puzzle", r"floor\b.*(live|stay|resident)", r"floor\s*based",
        r"schedule", r"comparison", r"order\s*and\s*ranking",
        r"ranking", r"order\s*based", r"sequence",
        r"different\s*floors", r"eight\s*people", r"seven\s*persons",
        r"five\s*persons?", r"box\b.*(contain|color)",
    )),
    ArchetypeDef("Number Series", "Reasoning", "both", "medium", (
        r"number\s*series", r"missing\s*number", r"next\s*number",
        r"series:\s*\d", r"what\s*comes\s*next", r"find\s*the\s*missing",
        r"complete\s*the\s*series", r"wrong\s*number", r"odd\s*one\s*out",
        r"\d+,\s*\d+,\s*\d+,\s*\d+",
    )),
    ArchetypeDef("Alphabet Series", "Reasoning", "both", "easy", (
        r"alphabet\s*series", r"letter\s*series", r"next\s*letter",
        r"english\s*alphabet", r"vowel", r"consonant",
        r"position\s*of\s*\w+\s*in", r"alphabetical\s*order",
        r"\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+",
    )),
    ArchetypeDef("Direction Sense", "Reasoning", "both", "easy", (
        r"direction", r"north", r"south", r"east\b", r"west\b",
        r"north.east", r"north.west", r"south.east", r"south.west",
        r"left\s*turn", r"right\s*turn", r"which\s*direction",
        r"how\s*far", r"distance\s*from\s*start",
        r"facing\s*(north|south)", r"walks?\s*\d+\s*(km|m|meter)",
    )),
    ArchetypeDef("Logical Reasoning", "Reasoning", "both", "medium", (
        r"logical\s*reasoning", r"statement.*argument", r"strengthen", r"weaken",
        r"assumption", r"inference", r"deduction", r"cause\s*and\s*effect",
        r"course\s*of\s*action", r"assertion", r"reason\b",
        r"if\s*.*then\s*(which|what)", r"based\s*on\s*the\s*information",
        r"true\s*statement", r"false\s*statement",
    )),
    ArchetypeDef("Venn Diagrams", "Reasoning", "both", "easy", (
        r"venn\s*diagram", r"best\s*represent", r"relationship\s*between",
        r"which\s*diagram", r"following\s*diagram",
    )),
    ArchetypeDef("Non-Verbal Reasoning", "Reasoning", "both", "medium", (
        r"non.verbal", r"figure\s*series", r"mirror\s*image", r"water\s*image",
        r"embedded\s*figure", r"paper\s*folding", r"paper\s*cutting",
        r"hidden\s*figure", r"complete\s*the\s*pattern",
        r"missing\s*figure", r"visual\s*reasoning",
        r"which\s*of\s*the\s*following\s*figures?",
        r"count\s*the\s*number\s*of\s*triangles",
        r"how\s*many\s*triangles",
    )),

    # ── English ─────────────────────────────────────────────────────
    ArchetypeDef("Reading Comprehension", "English", "both", "medium", (
        r"comprehension", r"passage", r"read\s*the\s*passage",
        r"according\s*to\s*the\s*passage", r"based\s*on\s*the\s*passage",
        r"the\s*passage\s*suggests?", r"author\s*of\s*the\s*passage",
        r"main\s*idea", r"central\s*theme",
        r"what\s*does\s*the\s*passage", r"the\s*passage\s*is\s*about",
    )),
    ArchetypeDef("Cloze Test", "English", "both", "medium", (
        r"cloze", r"fill\s*in\s*the\s*blanks?\s*in\s*the\s*passage",
        r"blank.*passage", r"passage.*blank",
        r"choose\s*the\s*correct\s*word\s*for\s*the\s*blank",
    )),
    ArchetypeDef("Fill in the Blanks", "English", "both", "easy", (
        r"fill\s*in\s*the\s*blank", r"blank\s*space", r"complete\s*the\s*sentence",
        r"sentence.*blank", r"choose\s*the\s*correct\s*word",
        r"appropriate\s*word", r"suitable\s*word",
        r"\w+\s*_\s*\w+", r"_\s*\w+\s*_",
    )),
    ArchetypeDef("Error Spotting", "English", "both", "medium", (
        r"error\s*spotting", r"error\s*detection", r"find\s*the\s*error",
        r"error\s*in\s*the\s*sentence", r"part\s*of\s*the\s*sentence",
        r"spot\s*the\s*error", r"incorrect\s*part",
        r"no\s*error", r"grammatical\s*error",
        r"which\s*part\s*of\s*the\s*sentence",
        r"identify\s*the\s*error",
        r"\w+/\s*\w+\s*/\s*\w+",
    )),
    ArchetypeDef("Sentence Improvement", "English", "both", "medium", (
        r"sentence\s*improvement", r"improve\s*the\s*sentence",
        r"better\s*way\s*to\s*write", r"replace\s*the\s*underlined",
        r"best\s*replacement", r"which\s*of\s*the\s*following\s*improves?",
        r"correct\s*form\s*of\s*the\s*sentence",
    )),
    ArchetypeDef("Synonyms & Antonyms", "English", "both", "easy", (
        r"synonym", r"antonym", r"opposite\s*in\s*meaning",
        r"similar\s*in\s*meaning", r"same\s*as",
        r"closest\s*in\s*meaning", r"most\s*similar",
        r"most\s*opposite", r"word\s*that\s*means",
        r"choose\s*the\s*word\s*that\s*is\s*(most\s*)?(similar|opposite)",
    )),
    ArchetypeDef("Active/Passive Voice", "English", "both", "hard", (
        r"active\s*voice", r"passive\s*voice", r"change\s*the\s*voice",
        r"change\s*into\s*(active|passive)",
        r"voice\s*change", r"convert\s*to\s*(active|passive)",
    )),
    ArchetypeDef("Direct/Indirect Speech", "English", "both", "hard", (
        r"direct\s*speech", r"indirect\s*speech", r"reported\s*speech",
        r"change\s*the\s*narration", r"narration\s*change",
        r"said\s*to\b", r"told\b.*that", r"asked\b.*that",
    )),
    ArchetypeDef("Idioms & Phrases", "English", "both", "medium", (
        r"idiom", r"phrase\s*meaning", r"meaning\s*of\s*the\s*idiom",
        r"give\s*the\s*meaning", r"replace\s*the\s*phrase",
        r"choose\s*the\s*correct\s*meaning\s*of\s*the\s*idiom",
    )),
    ArchetypeDef("One Word Substitution", "English", "both", "medium", (
        r"one\s*word\s*substitution", r"one\s*word\s*for",
        r"express\s*in\s*one\s*word", r"single\s*word",
        r"substitute\s*the\s*phrase\s*with\s*one\s*word",
    )),
    ArchetypeDef("Para Jumbles", "English", "both", "hard", (
        r"para\s*jumble", r"rearrange\s*the\s*sentence",
        r"rearrange\s*the\s*passage", r"correct\s*order\s*of\s*the\s*sentence",
        r"proper\s*sequence", r"meaningful\s*paragraph",
        r"order\s*of\s*sentences", r"sentence\s*rearrangement",
        r"re.order", r"rearrangement",
    )),
    ArchetypeDef("Spelling & Vocabulary", "English", "both", "easy", (
        r"spelling", r"correctly\s*spelled", r"incorrectly\s*spelled",
        r"misspelt", r"choose\s*the\s*correct\s*spelling",
        r"which\s*is\s*correctly\s*spelled",
    )),
    ArchetypeDef("Articles & Prepositions", "English", "both", "easy", (
        r"article\b", r"preposition", r"fill\s*in\s*with\s*(article|preposition)",
        r"appropriate\s*(article|preposition)",
        r"correct\s*(article|preposition)",
        r"a\s*an\s*the", r"in\s*on\s*at",
    )),

    # ── GK / GA ─────────────────────────────────────────────────────
    ArchetypeDef("Indian History", "GK/GA", "both", "medium", (
        r"history", r"ancient\s*india", r"medieval\s*india", r"modern\s*india",
        r"freedom\s*movement", r"indian\s*national\s*congress",
        r"battle\s*of", r"dynasty", r"empire", r"mughal", r"maurya",
        r"gupta", r"vedic", r"indus\s*valley", r"harappa",
        r"revolt\s*of\s*1857", r"constitution\s*assembly",
        r"governor.general", r"viceroy",
        r"independence", r"partition",
    )),
    ArchetypeDef("Indian Geography", "GK/GA", "both", "medium", (
        r"geography", r"river\b", r"mountain\s*range", r"himachal",
        r"western\s*ghats?", r"eastern\s*ghats?", r"plateau",
        r"climate\s*of\s*india", r"monsoon", r"soil\b", r"vegetation",
        r"wildlife", r"national\s*park", r"sanctuary",
        r"biosphere\s*reserve", r"lake\b", r"sea\b",
        r"capital\s*of\b", r"largest\s*state",
        r"borders?\s*of\s*india", r"neighboring\s*countr",
        r"longest\s*river", r"highest\s*peak",
    )),
    ArchetypeDef("Indian Polity", "GK/GA", "both", "medium", (
        r"polity", r"constitution", r"fundamental\s*rights?", r"directive\s*principle",
        r"fundamental\s*duties?", r"parliament", r"supreme\s*court",
        r"high\s*court", r"judiciary", r"executive", r"legislature",
        r"president\s*of\s*india", r"prime\s*minister\s*of\s*india",
        r"governor\b", r"chief\s*minister", r"panchayat",
        r"municipal", r"amendment", r"schedule",
        r"lok\s*sabha", r"rajya\s*sabha", r"bill\b",
        r"election\s*commission", r"finance\s*commission",
        r"article\s*\d+", r"union\s*list", r"state\s*list",
        r"concurrent\s*list",
    )),
    ArchetypeDef("Indian Economy", "GK/GA", "both", "medium", (
        r"economy", r"gdp\b", r"gnp\b", r"inflation", r"budget\b",
        r"five\s*year\s*plan", r"niti\s*aayog", r"planning\s*commission",
        r"reserve\s*bank\s*of\s*india", r"rbi\b",
        r"monetary\s*policy", r"fiscal\s*policy",
        r"tax\b", r"gst\b", r"direct\s*tax", r"indirect\s*tax",
        r"stock\s*exchange", r"sebi\b",
        r"liberalization", r"privatization", r"globalization",
        r"finance\s*minister", r"economic\s*survey",
    )),
    ArchetypeDef("General Science", "GK/GA", "both", "medium", (
        r"science", r"physics", r"chemistry", r"biology",
        r"law\s*of\s*motion", r"newton", r"electron", r"proton", r"neutron",
        r"acid\b", r"base\b", r"salt\b", r"chemical\s*reaction",
        r"periodic\s*table", r"element\b", r"compound\b",
        r"cell\b", r"tissue", r"organ\b", r"digestive\s*system",
        r"respiratory\s*system", r"circulatory\s*system",
        r"nervous\s*system", r"vitamin", r"mineral\b", r"protein",
        r"carbohydrate", r"hormone", r"enzyme",
        r"force\b", r"energy\b", r"heat\b", r"light\b", r"sound\b",
        r"electricity", r"magnet", r"nuclear",
        r"computer\s*(?!(knowledge|module))",
    )),
    ArchetypeDef("Current Affairs", "GK/GA", "both", "medium", (
        r"current\s*affairs", r"recently", r"202[0-9]", r"2024\b",
        r"scheme\b", r"mission\b", r"awarded\b",
        r"who\s*has\s*been\s*(appointed|elected|awarded|selected|honoured)",
        r"government\s*yojana", r"inaugurated",
        r"summit", r"conference\b",
    )),
    ArchetypeDef("Sports", "GK/GA", "both", "easy", (
        r"sport", r"olympic", r"world\s*cup", r"cricket",
        r"football", r"hockey", r"tennis", r"badminton",
        r"chess\b", r"asian\s*games", r"commonwealth\s*games",
        r"player\b.*(?:won|awarded|selected)",
        r"tournament", r"championship",
        r"medal", r"gold\s*medal",
        r"first\s*indian\b.*(?:to|in)",
    )),
    ArchetypeDef("Awards & Honors", "GK/GA", "both", "easy", (
        r"award", r"honour", r"bharat\s*ratna", r"padma\s*(shri|bhushan|vibhushan)",
        r"nobel\s*prize", r"gallantry\s*award",
        r"param\s*vir\s*chakra", r"ashoka\s*chakra",
        r"dadasaheb\s*phalke", r"oscar", r"grammy",
        r"book\s*of\s*the\s*year", r"man\s*booker",
        r"jananpith", r"sahitya\s*akademi",
    )),
    ArchetypeDef("Indian Culture", "GK/GA", "both", "medium", (
        r"culture", r"dance\s*(form|style)", r"classical\s*dance",
        r"folk\s*dance", r"music\b", r"instrument",
        r"festival\s*of\s*india", r"temple\b", r"monument",
        r"world\s*heritage\s*site", r"unesco",
        r"yoga\b", r"ayurveda",
        r"art\s*form", r"painting",
    )),
    ArchetypeDef("Days & Events", "GK/GA", "both", "easy", (
        r"observed\s*as", r"celebrated\s*as", r"international\s*day",
        r"national\s*day", r"world\s*day", r"world\s*health",
        r"environment\s*day", r"youth\s*day",
        r"when\s*is\b", r"falls\s*on\b",
    )),

    # ── Computer Knowledge ──────────────────────────────────────────
    ArchetypeDef("Computer Fundamentals", "Computer Knowledge", "both", "medium", (
        r"computer\b", r"cpu\b", r"memory\b", r"input\s*device",
        r"output\s*device", r"storage\b", r"operating\s*system",
        r"software", r"hardware", r"network\b",
        r"internet\b", r"browser", r"email\b",
        r"ms\s*office", r"excel\b", r"word\b.*(?!.*substitut)",
        r"powerpoint", r"database",
        r"virus\b", r"malware", r"firewall",
        r"binary", r"bit\b", r"byte\b", r"kilobyte",
        r"shortcut\s*key", r"keyboard\s*shortcut",
    )),
]
# fmt: on

# Compiled patterns
_COMPILED: list[tuple[str, str, str, str, re.Pattern]] = []
for ad in ARCHETYPE_DEFS:
    pattern = re.compile("|".join(ad.keywords), re.IGNORECASE)
    _COMPILED.append((ad.name, ad.section, ad.tier, ad.difficulty, pattern))


# ── Public API ────────────────────────────────────────────────────────


def classify_question(question: Question) -> str | None:
    """Classify a question into an archetype by keyword matching.

    Args:
        question: The question to classify.

    Returns:
        The archetype name, or None if no archetype matches.
    """
    text = f"{question.question_text} {' '.join(o.text for o in question.options)}"

    candidates: list[tuple[str, int]] = []  # (name, match_count)

    for name, section, _tier, _diff, pattern in _COMPILED:
        if section != question.section:
            continue
        matches = pattern.findall(text)
        if matches:
            candidates.append((name, len(matches)))

    if candidates:
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    return None


def assign_archetypes(
    db: Database,
    question_ids: list[str] | None = None,
    commit: bool = True,
) -> dict[str, int]:
    """Assign archetypes to questions in the database.

    For each question without an archetype_id (or the given subset),
    runs keyword classification and updates the database.

    Args:
        db: Database instance.
        question_ids: Optional subset of question IDs to process.
                       If None, processes all un-assigned questions.
        commit: Whether to commit after each batch.

    Returns:
        Dict with keys: assigned, skipped, unknown.
    """
    conn = db.connect()

    if question_ids:
        placeholders = ",".join("?" for _ in question_ids)
        rows = conn.execute(
            f"SELECT * FROM questions WHERE question_id IN ({placeholders})",
            question_ids,
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM questions WHERE archetype_id IS NULL"
        ).fetchall()

    assigned = 0
    unknown = 0

    for row in rows:
        question = _row_to_question_archetype(row)
        archetype_name = classify_question(question)

        if archetype_name is None:
            unknown += 1
            continue

        # Get or create archetype
        arch_id = _ensure_archetype(db, archetype_name, question.section)

        if arch_id:
            conn.execute(
                "UPDATE questions SET archetype_id = ? WHERE question_id = ?",
                (arch_id, question.question_id),
            )
            assigned += 1

    if commit:
        conn.commit()

    return {"assigned": assigned, "skipped": len(rows) - assigned - unknown, "unknown": unknown}


def ensure_default_archetypes(db: Database) -> int:
    """Create all defined archetypes in the database if they don't exist.

    Returns:
        Number of archetypes created.
    """
    created = 0
    conn = db.connect()

    for ad in ARCHETYPE_DEFS:
        existing = conn.execute(
            "SELECT archetype_id FROM archetypes WHERE name = ? AND section = ?",
            (ad.name, ad.section),
        ).fetchone()

        if not existing:
            conn.execute(
                """INSERT INTO archetypes (name, section, tier, difficulty)
                   VALUES (?, ?, ?, ?)""",
                (ad.name, ad.section, ad.tier, ad.difficulty),
            )
            created += 1

    if created:
        conn.commit()

    return created


def get_weak_archetypes(
    db: Database,
    min_attempts: int = 5,
    accuracy_threshold: float = 0.65,
) -> list[dict[str, Any]]:
    """Find archetypes where the user's accuracy is below threshold.

    Args:
        db: Database instance.
        min_attempts: Minimum number of attempts before considering.
        accuracy_threshold: Accuracy below this is "weak".

    Returns:
        List of dicts with keys: archetype_id, name, section, tier,
        attempts, correct, accuracy, suggested_focus.
    """
    conn = db.connect()

    rows = conn.execute(
        """SELECT a.archetype_id, a.name, a.section, a.tier,
                  COUNT(at.attempt_id) as attempt_count,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct_count
           FROM archetypes a
           LEFT JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           WHERE a.is_active = 1
           GROUP BY a.archetype_id
           HAVING attempt_count >= ?
           ORDER BY CAST(correct_count AS REAL) / attempt_count ASC""",
        (min_attempts,),
    ).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        attempts = row["attempt_count"] or 0
        correct = row["correct_count"] or 0
        accuracy = correct / attempts if attempts > 0 else 0.0

        if accuracy < accuracy_threshold:
            results.append({
                "archetype_id": row["archetype_id"],
                "name": row["name"],
                "section": row["section"],
                "tier": row["tier"],
                "attempts": attempts,
                "correct": correct,
                "accuracy": round(accuracy, 3),
                "suggested_focus": accuracy < 0.5,
            })

    return results


def get_archetype_questions(
    db: Database,
    archetype_id: int,
    count: int = 10,
    exclude_holdout: bool = True,
) -> list[dict[str, Any]]:
    """Get practice questions for a specific archetype.

    Args:
        db: Database instance.
        archetype_id: The archetype to pull from.
        count: Number of questions to return.
        exclude_holdout: Exclude holdout questions.

    Returns:
        List of dicts with question_id, question_text, tier.
    """
    conn = db.connect()
    where = "archetype_id = ?"
    params: list[Any] = [archetype_id]

    if exclude_holdout:
        where += " AND is_holdout = 0"

    rows = conn.execute(
        f"SELECT question_id, question_text, tier FROM questions WHERE {where} ORDER BY RANDOM() LIMIT ?",
        params + [count],
    ).fetchall()

    return [
        {"question_id": r["question_id"], "question_text": r["question_text"][:200],
         "tier": r["tier"]}
        for r in rows
    ]


def get_archetype_summary(db: Database) -> list[dict[str, Any]]:
    """Return a summary of all archetypes and their stats.

    Returns:
        List of dicts with archetype info, question_count, attempt_count, accuracy.
    """
    conn = db.connect()
    rows = conn.execute(
        """SELECT a.archetype_id, a.name, a.section, a.tier, a.difficulty,
                  a.is_unlocked, a.is_active,
                  COUNT(DISTINCT q.question_id) as question_count,
                  COUNT(DISTINCT at.attempt_id) as attempt_count,
                  SUM(CASE WHEN at.is_correct = 1 THEN 1 ELSE 0 END) as correct_count
           FROM archetypes a
           LEFT JOIN questions q ON q.archetype_id = a.archetype_id
           LEFT JOIN attempts at ON at.question_id = q.question_id
           GROUP BY a.archetype_id
           ORDER BY a.section, a.name"""
    ).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        attempts = row["attempt_count"] or 0
        correct = row["correct_count"] or 0
        accuracy = round(correct / attempts, 3) if attempts > 0 else None

        results.append({
            "archetype_id": row["archetype_id"],
            "name": row["name"],
            "section": row["section"],
            "tier": row["tier"],
            "difficulty": row["difficulty"],
            "is_unlocked": bool(row["is_unlocked"]),
            "is_active": bool(row["is_active"]),
            "question_count": row["question_count"] or 0,
            "attempts": attempts,
            "accuracy": accuracy,
        })

    return results


# ── Internal helpers ──────────────────────────────────────────────────


def _ensure_archetype(db: Database, name: str, section: str) -> int | None:
    """Get or create an archetype, returning its ID."""
    conn = db.connect()
    row = conn.execute(
        "SELECT archetype_id FROM archetypes WHERE name = ? AND section = ?",
        (name, section),
    ).fetchone()

    if row:
        return row["archetype_id"]

    # Find matching definition
    tier = "both"
    difficulty = "medium"
    for ad in ARCHETYPE_DEFS:
        if ad.name == name and ad.section == section:
            tier = ad.tier
            difficulty = ad.difficulty
            break

    conn.execute(
        "INSERT INTO archetypes (name, section, tier, difficulty) VALUES (?, ?, ?, ?)",
        (name, section, tier, difficulty),
    )
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def _row_to_question_archetype(row: Any) -> Question:
    """Convert a DB row to a Question (minimal fields for classification)."""
    import json as _json

    from .models import Option as _Option

    options_data = _json.loads(row["options_json"]) if isinstance(row["options_json"], str) else []
    options = [_Option(label=o["label"], text=o["text"]) for o in options_data]

    def _g(key: str, default: Any = "") -> Any:
        try:
            v = row[key]
            return v if v is not None else default
        except (KeyError, IndexError):
            return default

    return Question(
        question_id=row["question_id"],
        pdf_name=_g("pdf_name", ""),
        source_page=_g("source_page", 0),
        global_question_number=_g("global_question_number", 0),
        section=row["section"],
        year=_g("year", 0),
        tier=_g("tier", "tier1"),
        question_text=row["question_text"],
        options=options,
        correct_option_label=_g("correct_option_label", ""),
    )

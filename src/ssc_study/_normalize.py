"""Section name normalization — maps raw PDF section names to 5 canonical categories."""

from __future__ import annotations

# Canonical section names
QUANT_DI = "Quant/DI"
REASONING = "Reasoning"
ENGLISH = "English"
GK_GA = "GK/GA"
COMPUTER_KNOWLEDGE = "Computer Knowledge"

CANONICAL_ORDER = [QUANT_DI, REASONING, ENGLISH, GK_GA, COMPUTER_KNOWLEDGE]

# Mapping from raw section names (as extracted from PDFs) to canonical sections.
NORMALIZE_MAP: dict[str, str] = {
    # Quant / DI
    "Quantitative Aptitude": QUANT_DI,
    "Quantitative abilities": QUANT_DI,
    "Mathematical Abilities": QUANT_DI,
    "Module I Mathematical Abilities": QUANT_DI,
    "Maths and Reasoning": QUANT_DI,
    "Statistics": QUANT_DI,
    "quant": QUANT_DI,
    "quantitative_aptitude": QUANT_DI,
    "Quant": QUANT_DI,
    "Module I: Mathematical Abilities": QUANT_DI,
    # Reasoning
    "General Intelligence and Reasoning": REASONING,
    "Reasoning": REASONING,
    "Reasoning and General Intelligence": REASONING,
    "Module II Reasoning and General Intelligence": REASONING,
    "Number Classification": REASONING,
    "Reasoning (Number Classification)": REASONING,
    "general_intelligence_and_reasoning": REASONING,
    "Module II: Reasoning and General Intelligence": REASONING,
    # English
    "English": ENGLISH,
    "English Language": ENGLISH,
    "English Comprehension": ENGLISH,
    "English Language and Comprehension": ENGLISH,
    "English and GA": ENGLISH,
    "Module I English Language and Comprehension": ENGLISH,
    "Comprehension": ENGLISH,
    "english": ENGLISH,
    "english_comprehension": ENGLISH,
    "english_language_and_comprehension": ENGLISH,
    "Module I: English Language and Comprehension": ENGLISH,
    # GK / GA
    "General Awareness": GK_GA,
    "Module II General Awareness": GK_GA,
    "general_awareness": GK_GA,
    "general_knowledge": GK_GA,
    "Module II: General Awareness": GK_GA,
    # Computer Knowledge
    "Computer": COMPUTER_KNOWLEDGE,
    "Computer Knowledge Module": COMPUTER_KNOWLEDGE,
    "Module I Computer Knowledge Module": COMPUTER_KNOWLEDGE,
    "computer_knowledge": COMPUTER_KNOWLEDGE,
    "Module I: Computer Knowledge Module": COMPUTER_KNOWLEDGE,
}


def normalize_section(raw: str) -> str:
    """Normalize a raw section name to its canonical form.

    Args:
        raw: The section name from the merged JSON or PDF extraction.

    Returns:
        One of: 'Quant/DI', 'Reasoning', 'English', 'GK/GA', 'Computer Knowledge'.
        Returns the input unchanged if no mapping exists (with warning).
    """
    if not raw:
        return QUANT_DI  # default fallback
    key = raw.strip()
    if key in NORMALIZE_MAP:
        return NORMALIZE_MAP[key]
    # Try case-insensitive match
    key_lower = key.lower()
    for k, v in NORMALIZE_MAP.items():
        if k.lower() == key_lower:
            return v
    return key  # unmapped — caller should handle


def infer_section_from_qnum(
    global_qnum: int,
    tier: str,
    pdf_name: str = "",
) -> str:
    """Infer section from global question number using standard SSC CGL format.

    Tier 1 standard format (100 questions):
        Q1-25  → Reasoning
        Q26-50 → GK/GA
        Q51-75 → Quant/DI
        Q76-100 → English

    Tier 2 depends on the paper name. Subject-specific PDFs map all questions
    to that subject. Multi-subject paper 1 uses a different distribution.
    """
    pdf_lower = pdf_name.lower()

    # Subject-specific Tier 2 PDFs
    if "english" in pdf_lower and "tier2" in pdf_lower:
        return ENGLISH
    if "quant" in pdf_lower and "tier2" in pdf_lower:
        return QUANT_DI

    if tier == "tier1":
        if 1 <= global_qnum <= 25:
            return REASONING
        elif 26 <= global_qnum <= 50:
            return GK_GA
        elif 51 <= global_qnum <= 75:
            return QUANT_DI
        elif 76 <= global_qnum <= 100:
            return ENGLISH
    else:
        # Tier 2 multi-subject paper 1 varies by year
        if "appx_answer_key" in pdf_lower:
            return QUANT_DI  # answer key is mostly quant
        if global_qnum <= 30:
            return QUANT_DI
        elif global_qnum <= 60:
            return REASONING
        elif global_qnum <= 100:
            return ENGLISH
        else:
            return GK_GA

    return QUANT_DI  # fallback


def get_pdf_year_tier(pdf_name: str) -> tuple[int, str]:
    """Extract year and tier from a PDF directory name.

    Args:
        pdf_name: e.g. "2021_tier1_prepp_shift1" or "2024_tier2_prepp_paper1"

    Returns:
        (year, tier) tuple, e.g. (2021, 'tier1')
    """
    parts = pdf_name.split("_")
    year = int(parts[0]) if parts and parts[0].isdigit() else 0
    tier = "tier1" if "tier1" in pdf_name.lower() else "tier2"
    return year, tier

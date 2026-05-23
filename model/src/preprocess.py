"""
================================================================================
PHARMABOT PH — Text Preprocessing Pipeline
================================================================================
Provides text cleaning, normalization, and tokenization utilities for both
classical ML classifiers (NB, LR) and LLM tokenizers (BPE / SentencePiece).

Key Features:
- Unicode normalization (NFKD)
- HTML tag stripping
- Dosage unit normalization (e.g., "500mg" → "500 mg")
- Philippine peso price normalization (e.g., "P50" → "₱ 50")
- PH brand-to-generic drug name normalization
- NLTK tokenization + lemmatization for classical models
- Special preservation of medical negation and qualifier tokens
================================================================================
"""

import re
import unicodedata
from typing import List

# ------------------------------------------------------------------------------
# NLTK setup (lazy download on first use)
# ------------------------------------------------------------------------------
import nltk

_nltk_initialized = False


def _ensure_nltk():
    """Download required NLTK data if not already present."""
    global _nltk_initialized
    if _nltk_initialized:
        return
    for pkg in ["punkt", "punkt_tab", "stopwords", "wordnet", "averaged_perceptron_tagger"]:
        try:
            if pkg in ("punkt", "punkt_tab"):
                nltk.data.find(f"tokenizers/{pkg}")
            else:
                nltk.data.find(f"corpora/{pkg}")
        except LookupError:
            nltk.download(pkg, quiet=True)
    _nltk_initialized = True


# ------------------------------------------------------------------------------
# Critical pharma tokens that must NOT be removed by stopword filtering
# ------------------------------------------------------------------------------
PHARMA_PRESERVE_TOKENS = {
    "not", "no", "never", "only", "without", "avoid",
    "do", "don't", "stop", "before", "after", "during",
    "allergy", "allergic", "pregnant", "breastfeeding",
}

# ------------------------------------------------------------------------------
# Taglish -> English symptom mapping (helps BM25 retrieval)
# ------------------------------------------------------------------------------
_TAGLISH_SYMPTOM_MAP = {
    # --- Fever / General illness ---
    "lagnat": "fever",
    "nilalagnat": "fever",
    "may lagnat": "fever",
    "mainit sa pakiramdam": "feverish",
    "giniginaw": "chills",
    "panginginig": "chills",
    "trangkaso": "flu",
    "may trangkaso": "flu",
    "nilalabanan ang sakit": "fighting illness",
    "pagkapagod": "fatigue",
    "pagod": "tiredness",
    "panghihina": "weakness",
    "pawis": "sweating",
    "pagpapawis": "sweating",
    "pasmado": "sweaty palms",
    "pasmang kamay": "sweaty hands",
    "pasmang paa": "sweaty feet",

    # --- Head & neurological ---
    "masakit ang ulo": "headache",
    "sakit ng ulo": "headache",
    "matinding sakit ng ulo": "severe headache",
    "tinusok ang ulo": "stabbing headache",
    "pananakit ng ulo na paulit-ulit": "recurring headache",
    "migraine": "migraine",
    "hilo": "dizziness",
    "nahihilo": "feeling dizzy",
    "vertigo": "dizziness",
    "init ng ulo": "irritability",
    "pagkainis": "irritability",
    "pagkawala ng gana": "loss of appetite",
    "manhid": "numbness",
    "pamamanhid": "numbness",
    "pamamanhid ng kamay": "hand numbness",
    "pamamanhid ng paa": "foot numbness",
    "manhid ang kamay": "hand numbness",
    "manhid ang paa": "foot numbness",
    "tagilid ang pakiramdam": "feeling off-balance",
    "hindi makatulog": "insomnia",
    "puyat": "lack of sleep",
    "panaginip": "nightmares",
    "pagkabalisa sa gabi": "night anxiety",
    "pag-aalala": "anxiety",
    "pagkabalisa": "anxiety",
    "panlulumo": "depression",
    "pagkawala ng panlasa": "loss of taste",
    "hindi makaamoy": "loss of smell",

    # --- Respiratory ---
    "ubo": "cough",
    "ubo na may plema": "productive cough",
    "ubo na tuyo": "dry cough",
    "ubo na may dugo": "hemoptysis",
    "sipon": "runny nose",
    "suob": "nasal congestion",
    "baradong ilong": "nasal congestion",
    "hirap huminga": "difficulty breathing",
    "mahirap huminga": "difficulty breathing",
    "panghihingal": "shortness of breath",
    "mabilis ang paghinga": "rapid breathing",
    "ubong may tunog": "wheezing",
    "mabigat ang dibdib": "chest tightness",
    "pananakit ng dibdib": "chest pain",
    "palpitasyon": "palpitations",
    "hika": "asthma",
    "hika na sumusuko": "asthma attack",
    "sakit ng lalamunan": "sore throat",
    "baradong lalamunan": "sore throat",
    "tonsilitis": "tonsillitis",
    "tonsilit": "tonsillitis",
    "tuyong lalamunan": "dry throat",
    "pangangati ng lalamunan": "itchy throat",

    # --- GI / stomach ---
    "masakit ang tiyan": "stomach ache",
    "sakit ng tiyan": "stomach pain",
    "masakit ang tiyan pagkatapos kumain": "stomach pain after eating",
    "pagtatae": "diarrhea",
    "loose bowel": "diarrhea",
    "maduming dumi": "bloody stool",
    "pagsusuka": "vomiting",
    "nagususuka": "vomiting",
    "sikmura": "nausea",
    "nagduduwal": "feeling nauseous",
    "maasim ang tiyan": "sour stomach",
    "heartburn": "heartburn",
    "hyperacidity": "hyperacidity",
    "acidity": "acid reflux",
    "acid": "acid reflux",
    "mabigat ang tiyan": "bloating",
    "kabag": "gas",
    "pag-utot": "gas",
    "hirap dumumi": "constipation",
    "hindi nakakadumi": "constipation",
    "constipation": "constipation",
    "almoranas": "hemorrhoids",
    "pagkabalisa ng sikmura": "stomach queasiness",
    "masakit ang tiyan sa bandang kanan": "right side abdominal pain",
    "masakit ang tiyan sa bandang kaliwa": "left side abdominal pain",
    "masakit ang tiyan sa itaas": "upper abdominal pain",
    "masakit ang tiyan sa baba": "lower abdominal pain",

    # --- Skin ---
    "pantal": "rash",
    "pantal sa balat": "skin rash",
    "pamamantal sa balat": "skin irritation",
    "pangangati": "itchy",
    "pangangati ng balat": "itchy skin",
    "pangangati sa paa": "athlete's foot symptom",
    "namumula": "redness",
    "namumula ang balat": "skin redness",
    "sunog": "sunburn",
    "pigsa": "boil",
    "buni": "hives",
    "buni sa balat": "hives",
    "an-an": "tinea versicolor",
    "an-an sa balat": "tinea versicolor",
    "hadhad": "jock itch",
    "galis": "scabies",
    "kalyo": "corns",
    "kalyo sa paa": "foot corns",
    "kalyo sa kamay": "hand calluses",
    "paltos": "blister",
    "pekas": "melasma",
    "balakubak": "dandruff",
    "pangingitim": "bruising",
    "pangingitim ng kuko": "nail discoloration",
    "sugat": "wound",
    "sugat na naninilaw": "infected wound",
    "sugat na hindi gumagaling": "non-healing wound",
    "kinati ng insecto": "insect bite",
    "pasa": "bruise",

    # --- Eyes / ENT ---
    "sore eyes": "conjunctivitis",
    "pulang mata": "red eyes",
    "naglalagkit ang mata": "eye discharge",
    "magang mata": "puffy eyes",
    "pangangati ng mata": "itchy eyes",
    "baradong tenga": "ear congestion",
    "tagpi sa tenga": "earwax",
    "singaw": "mouth sores",
    "ngala-ngala": "mouth ulcer",
    "bukol sa gilagid": "gum swelling",
    "pangil": "toothache",
    "sakit ng ngipin": "toothache",
    "bulutong": "mumps",

    # --- Musculoskeletal ---
    "masakit ang likod": "back pain",
    "masakit ang likuran": "lower back pain",
    "masakit ang baywang": "waist pain",
    "masakit ang balakang": "hip pain",
    "masakit ang tuhod": "knee pain",
    "masakit ang balikat": "shoulder pain",
    "masakit ang leeg": "neck pain",
    "masakit ang binti": "leg pain",
    "masakit ang braso": "arm pain",
    "rayuma": "joint pain",
    "rayuma sa kamay": "hand joint pain",
    "rayuma sa tuhod": "knee joint pain",
    "rayuma sa balikat": "shoulder joint pain",
    "nangangalawang": "muscle soreness",
    "pangangalawang": "muscle pain",
    "pagkirot": "sharp pain",
    "kurot": "cramps",
    "pasma": "muscle cramps",
    "lamig": "muscle stiffness",
    "nangangalay": "muscle fatigue",
    "pilay": "sprain",
    "bukol": "lump",
    "pamamaga": "swelling",
    "namamanas": "edema",
    "manas": "edema",
    "pamamanas ng paa": "foot swelling",
    "pamamanas ng kamay": "hand swelling",
    "bali": "fracture",

    # --- Chronic / systemic ---
    "tumaas ang blood sugar": "high blood sugar",
    "mataas ang presyon": "high blood pressure",
    "mataas ang bp": "hypertension",
    "mababa ang blood sugar": "low blood sugar",
    "mahina ang puso": "heart weakness",
    "tumataba": "weight gain",
    "pumapayat": "weight loss",

    # --- Women's / pediatric ---
    "sakit ng puson": "dysmenorrhea",
    "masakit ang puson": "dysmenorrhea",
    "dysmenorrhea": "dysmenorrhea",
    "regla": "menstruation",
    "irregular na regla": "irregular menstruation",
    "delay na regla": "delayed menstruation",
    "taghiyawat": "acne",
    "taghiyawat sa mukha": "facial acne",
    "taghiyawat sa noo": "forehead acne",
    "pamamaga ng suso": "breast tenderness",
    "pagngarag ng ngipin": "teething",
    "iyak ng baby na hindi matigil": "infant colic",
    "kabag ng baby": "colic",
    "paglilihi": "morning sickness",
    "suka ng buntis": "morning sickness",
    "pamamaga ng paa sa buntis": "pregnancy edema",
    "pagdudumi ng buntis": "pregnancy constipation",
    "pangangati ng ari ng buntis": "pregnancy yeast infection",
    "pamamaga ng ngipin sa buntis": "pregnancy gingivitis",
}


def translate_taglish_symptoms(text: str) -> str:
    """Replace common Taglish symptom terms with English equivalents for BM25."""
    text_lower = text.lower()
    for taglish, english in _TAGLISH_SYMPTOM_MAP.items():
        if taglish in text_lower:
            text = text.replace(taglish, english, 1)
    return text


def clean_pharma_text(text: str) -> str:
    """
    ================================================================================
    Core pharmaceutical text cleaner.
    ================================================================================
    Steps:
        1. Unicode NFKD normalization
        2. Lowercasing
        3. HTML tag stripping
        4. Dosage unit normalization (e.g., 500mg → 500 mg)
        5. Peso price normalization (e.g., P50, php50 → ₱ 50)
        6. Special character filtering (retain medical-relevant chars)
        7. Whitespace collapse
    ================================================================================
    """
    if not isinstance(text, str):
        text = str(text)

    # 1. Unicode normalization
    text = unicodedata.normalize("NFKD", text)

    # 2. Lowercase
    text = text.lower()

    # 3. Strip HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # 4. Normalize dosage units: 500mg, 10ml, 250mcg → 500 mg, 10 ml, 250 mcg
    text = re.sub(
        r"(\d+(?:\.\d+)?)(mg|ml|mcg|g\b|iu|units?)",
        r"\1 \2",
        text,
        flags=re.IGNORECASE,
    )

    # 5. Normalize peso prices: ₱50, P50, php50, Php 100 → ₱ 50, ₱ 100
    text = re.sub(r"[₱pP][hH]?[pP]?\s*(\d+)", r"₱ \1", text)

    # 6. Retain only alphanumeric, spaces, and medical-relevant punctuation
    text = re.sub(r"[^\w\s\(\)\-\/\.\₱%]", " ", text)

    # 7. Collapse multiple whitespaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def full_preprocess(text: str, for_lm: bool = False) -> str | List[str]:
    """
    ================================================================================
    Full preprocessing pipeline.
    ================================================================================
    Args:
        text (str): Raw input string.
        for_lm (bool):
            - False → returns list of cleaned, lemmatized tokens for classical ML.
            - True  → returns cleaned string ready for LLM tokenizer (BPE/SentencePiece).

    Returns:
        str | List[str]: Cleaned string (for_lm=True) or token list (for_lm=False).
    ================================================================================
    """
    from src.ph_drug_map import normalize_ph_drug_names

    # Step 1: Base cleaning
    text = clean_pharma_text(text)

    # Step 2: PH brand → generic normalization
    text = normalize_ph_drug_names(text)

    # For LLM tokenizers, return the cleaned string directly
    if for_lm:
        return text

    # Step 3: Classical ML pipeline (tokenize + lemmatize + filter)
    _ensure_nltk()
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    stop_words = set(stopwords.words("english"))
    # Remove critical medical qualifiers from stopwords
    stop_words -= PHARMA_PRESERVE_TOKENS

    lemmatizer = WordNetLemmatizer()

    tokens = word_tokenize(text)
    tokens = [
        lemmatizer.lemmatize(t)
        for t in tokens
        if (t.isalpha() or t in PHARMA_PRESERVE_TOKENS)
        and (t not in stop_words or t in PHARMA_PRESERVE_TOKENS)
    ]
    return tokens


def preprocess_for_llm_tokenizer(text: str) -> str:
    """
    ================================================================================
    Convenience wrapper that returns a string ready for the LLM tokenizer.
    ================================================================================
    """
    return full_preprocess(text, for_lm=True)


def preprocess_for_classical_ml(text: str) -> List[str]:
    """
    ================================================================================
    Convenience wrapper that returns a token list for NB / LR / TF-IDF.
    ================================================================================
    """
    return full_preprocess(text, for_lm=False)


# ------------------------------------------------------------------------------
# Chat Template Helpers (TinyLlama / Llama-2 style)
# ------------------------------------------------------------------------------
def format_chat_prompt(
    system_message: str,
    user_message: str,
    retrieved_context: str = "",
    tokenizer=None,
) -> str:
    """
    ================================================================================
    Format a chat prompt using the model's native chat template.
    ================================================================================
    Args:
        system_message (str): System instruction text.
        user_message (str): User query.
        retrieved_context (str): BM25-retrieved drug context (optional).
        tokenizer: HuggingFace tokenizer (optional). If provided, uses the
                   tokenizer's apply_chat_template for exact formatting.

    Returns:
        str: Formatted prompt string.
    ================================================================================
    """
    context_block = f"\n[Retrieved Drug Context]\n{retrieved_context.strip()}" if retrieved_context.strip() else ""

    messages = [
        {"role": "system", "content": system_message.strip() + context_block},
        {"role": "user", "content": user_message.strip()},
    ]

    if tokenizer is not None and hasattr(tokenizer, "apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )
        except Exception:
            pass

    # Fallback manual formatting (TinyLlama / Llama-2 style)
    prompt = (
        f"<|system|>\n{system_message.strip()}{context_block}</s>\n"
        f"<|user|>\n{user_message.strip()}</s>\n"
        f"<|assistant|>\n"
    )
    return prompt


if __name__ == "__main__":
    import sys, os
    _root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    # --- Sanity Checks ---
    sample_text = "Take Biogesic 500mg every 6 hours. Price is P50 per tablet."
    print("=" * 70)
    print("PREPROCESS SANITY CHECKS")
    print("=" * 70)
    print(f"\nOriginal: {sample_text}")
    cleaned = clean_pharma_text(sample_text).replace(chr(0x20b1), "PHP")
    print(f"Cleaned:  {cleaned}")
    print(f"For LM:   {preprocess_for_llm_tokenizer(sample_text).replace(chr(0x20b1), 'PHP')}")
    print(f"For ML:   {preprocess_for_classical_ml(sample_text)}")

    # Chat prompt demo
    print("\n" + "=" * 70)
    print("CHAT PROMPT FORMAT DEMO")
    print("=" * 70)
    demo_prompt = format_chat_prompt(
        system_message="You are Pharmacare, a pharmaceutical assistant.",
        user_message="What can I take for headache?",
        retrieved_context="Drug: Paracetamol | OTC | Price: PHP 1.50 - PHP 4.00",
    )
    print(demo_prompt)

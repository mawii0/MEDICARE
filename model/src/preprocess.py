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
    "lagnat": "fever",
    "ubo": "cough",
    "sipon": "runny nose",
    "masakit ang ulo": "headache",
    "masakit ang tiyan": "stomach pain",
    "pagtatae": "diarrhea",
    "sakit ng tiyan": "stomach pain",
    "sakit ng ulo": "headache",
    "sakit ng ngipin": "toothache",
    "pangangati": "itchy",
    "pantal": "rash",
    "pamamaga": "swelling",
    "suob": "nasal congestion",
    "baradong ilong": "nasal congestion",
    "hirap huminga": "difficulty breathing",
    "pananakit ng dibdib": "chest pain",
    "pagsusuka": "vomiting",
    "panghihina": "weakness",
    "pagkapagod": "fatigue",
    "pangangalawang": "muscle pain",
    "rayuma": "joint pain",
    "pasma": "muscle cramps",
    "binat": "relapse",
    "trangkaso": "flu",
    "trangkaso": "influenza",
    "sore eyes": "conjunctivitis",
    "pangangati ng mata": "itchy eyes",
    "panginginig": "chills",
    "pawis": "sweating",
    "sakit ng lalamunan": "sore throat",
    "baradong tenga": "ear congestion",
    "vertigo": "dizziness",
    "hilo": "dizziness",
    "pangangati ng balat": "itchy skin",
    "pantal sa balat": "skin rash",
    "sunog": "sunburn",
    "kabag": "gas",
    "heartburn": "heartburn",
    "hyperacidity": "hyperacidity",
    "acidity": "acid reflux",
    "acid": "acid reflux",
    "pigsa": "boil",
    "almoranas": "hemorrhoids",
    "kinati ng insecto": "insect bite",
    "sugat": "wound",
    "pasa": "bruise",
    "sakit ng puson": "dysmenorrhea",
    "dysmenorrhea": "dysmenorrhea",
    # English symptom synonyms → terms that appear in drug full_text
    "stomach ache": "stomach pain",
    "stomach aches": "stomach pain",
    "stomach cramp": "stomach pain",
    "stomach cramps": "stomach pain",
    "tummy ache": "stomach pain",
    "tummy pain": "stomach pain",
    "belly pain": "stomach pain",
    "belly ache": "stomach pain",
    "abdominal cramp": "stomach pain",
    "abdominal cramps": "stomach pain",
    "back pain": "pain inflammation",
    "back ache": "pain inflammation",
    "body pain": "pain inflammation",
    "body ache": "pain inflammation",
    "muscle ache": "muscle pain",
    "tooth ache": "toothache",
    "throat pain": "sore throat",
    "runny nose": "nasal congestion",
    "stuffy nose": "nasal congestion",
    "clogged nose": "nasal congestion",
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

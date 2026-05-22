"""
================================================================================
PHARMABOT PH — Guardrails & Safety Layer
================================================================================
Implements:
    1. Emergency keyword detection (rule-based, immediate escalation)
    2. Intent routing (load saved classifiers)
    3. Rx restriction enforcement (post-generation injection)
    4. Mandatory disclaimer appending
    5. Language detection (simple heuristic for response language matching)
================================================================================
"""

import sys, os
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import re
import json
from typing import Dict, List, Any

import joblib
import numpy as np

from src.preprocess import preprocess_for_classical_ml
from src.ph_drug_map import normalize_ph_drug_names

# ------------------------------------------------------------------------------
# EMERGENCY KEYWORDS (Bilingual: English + Filipino/Taglish)
# ------------------------------------------------------------------------------
EMERGENCY_KEYWORDS = [
    # English
    "can't breathe", "cannot breathe", "difficulty breathing", "chest pain",
    "severe chest pain", "heart attack", "stroke", "seizure", "convulsion",
    "unconscious", "not responding", "severe bleeding", "uncontrolled bleeding",
    "overdose", "took too many pills", "swallowed pills", "poisoning",
    "anaphylaxis", "severe allergic reaction", "swelling face", "swelling throat",
    "suicide", "self-harm", "passed out", "fainted", "difficulty speaking",
    "numbness", "paralysis", "blue lips", "blue face", "choking",
    # Filipino / Taglish
    "hindi makahinga", "nahihirapan huminga", "masakit ang dibdib", "matinding sakit sa dibdib",
    "atake sa puso", "stroke", "seizure", "nag-seizure", "hindi mulat", "hindi gumagalaw",
    "matinding dugo", "sobrang pagkain ng gamot", "overdose sa gamot", "nalason",
    "allergic reaction", "namamaga ang mukha", "namamaga ang lalamunan",
    "pagpapakamatay", "nagpapakamatay", "nahimatay", "nahihilo", "nahihirap magsalita",
    "manhid", "paralisis", "asul ang labi", "nagba-baril", "nauubusan ng hangin",
]

EMERGENCY_RESPONSE_EN = (
    "⚠️ EMERGENCY DETECTED. The symptoms you described may require immediate medical attention.\n\n"
    "Please do the following immediately:\n"
    "1. Call 911 or go to the nearest hospital emergency room.\n"
    "2. Red Cross Philippines: 143\n"
    "3. DOH Hotline: 1555\n\n"
    "Do not attempt to self-medicate or wait. Seek professional help right away."
)

EMERGENCY_RESPONSE_TL = (
    "⚠️ EMERGENCY. Ang mga sintomas na iyong inilarawan ay maaaring mangailangan ng agarang medikal na tulong.\n\n"
    "Mangyaring gawin agad ang mga sumusunod:\n"
    "1. Tumawag sa 911 o pumunta sa pinakamalapit na emergency room ng ospital.\n"
    "2. Red Cross Philippines: 143\n"
    "3. DOH Hotline: 1555\n\n"
    "Huwag subukang mag-self-medicate o mag-antay. Humingi agad ng tulong sa propesyonal."
)

# ------------------------------------------------------------------------------
# DISCLAIMER TEXTS
# ------------------------------------------------------------------------------
DISCLAIMER_EN = (
    "\n\n---\n"
    "Disclaimer: This information is for general educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Always consult a licensed physician or "
    "pharmacist before taking any medication."
)

DISCLAIMER_TL = (
    "\n\n---\n"
    "Disclaimer: Ang impormasyong ito ay para lamang sa pangkalahatang edukasyon at hindi kapalit "
    "ng propesyonal na medikal na payo, diagnosis, o pagpapagamot. Laging kumonsulta sa lisensyadong "
    "doktor o parmasista bago uminom ng anumang gamot."
)

# ------------------------------------------------------------------------------
# RX RESTRICTION NOTES
# ------------------------------------------------------------------------------
RX_NOTE_EN = (
    "\n\n⚠️ PRESCRIPTION REQUIRED: This medicine requires a valid prescription from a licensed physician "
    "in the Philippines. It cannot be purchased without a prescription at any licensed pharmacy. "
    "Please consult your doctor for proper diagnosis and prescription before obtaining or taking this medication."
)

RX_NOTE_TL = (
    "\n\n⚠️ PRESCRIPTION REQUIRED: Ang gamot na ito ay nangangailangan ng valid na reseta mula sa lisensyadong doktor "
    "sa Pilipinas. Hindi maaaring bilhin nang walang reseta sa anumang lisensyadong parmasya. "
    "Mangyaring kumonsulta sa iyong doktor para sa tamang diagnosis at reseta bago kumuha o uminom ng gamot na ito."
)

CONTROLLED_NOTE_EN = (
    "\n\n⚠️ CONTROLLED SUBSTANCE (RA 9165): This medicine is classified as a dangerous drug under Republic Act 9165. "
    "It requires a special S2 prescription and strict regulatory compliance. Possession or distribution without proper "
    "authorization is a criminal offense in the Philippines."
)

CONTROLLED_NOTE_TL = (
    "\n\n⚠️ CONTROLLED SUBSTANCE (RA 9165): Ang gamot na ito ay klasipikadong dangerous drug sa ilalim ng Republic Act 9165. "
    "Nangangailangan ito ng espesyal na S2 prescription at mahigpit na regulatory compliance. "
    "Ang pagmamay-ari o distribusyon nang walang tamang awtorisasyon ay isang krimen sa Pilipinas."
)

# ------------------------------------------------------------------------------
# LANGUAGE DETECTION (Simple Heuristic)
# ------------------------------------------------------------------------------
def detect_language(text: str) -> str:
    """
    ================================================================================
    Simple heuristic to detect if a query is primarily English or Taglish/Filipino.
    ================================================================================
    Returns:
        "en" or "tl"
    ================================================================================
    """
    # Common Filipino / Taglish words / particles
    filipino_markers = [
        "ano", "ang", "sa", "ng", "mga", "ko", "mo", "niya", "sila", "tayo", "kayo",
        "ako", "ikaw", "siya", "ito", "iyan", "iyon", "namin", "natin", "nyo",
        "ba", "po", "ho", "opo", "hindi", "oo", "walang", "meron", "wala",
        "gamot", "sakit", "masakit", "lagnat", "ubo", "sipon", "tiyan", "ulo",
        "doktor", "ospital", "reseta", "presyo", "magkano", "saan", "paano",
        "pwede", "pweding", "pwede bang", "puede", "pwidi", "bawal", "dapat",
        "naman", "kasi", "daw", "raw", "din", "rin", "lang", "lng", "nag",
        "um", "in", "an", "pag", "pang",
    ]
    text_lower = text.lower()
    score = sum(1 for marker in filipino_markers if marker in text_lower)
    # Threshold: if 2+ Filipino markers, classify as Taglish/Filipino
    return "tl" if score >= 2 else "en"


# ------------------------------------------------------------------------------
# CLASSIFIER INTERFACE (loads persisted models)
# ------------------------------------------------------------------------------
class ClassifierInterface:
    """
    ================================================================================
    Loads saved ComplementNB (intent) and LogisticRegression (OTC/Rx) models
    and exposes a unified predict() method.
    ================================================================================
    """

    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.intent_clf = joblib.load(os.path.join(model_dir, "intent_clf.pkl"))
        self.rx_clf = joblib.load(os.path.join(model_dir, "rx_clf.pkl"))
        self.tfidf = joblib.load(os.path.join(model_dir, "tfidf_vectorizer.pkl"))
        self.rx_tfidf = joblib.load(os.path.join(model_dir, "rx_tfidf_vectorizer.pkl"))
        self.le = joblib.load(os.path.join(model_dir, "label_encoder.pkl"))

    def predict(self, raw_query: str) -> Dict[str, Any]:
        """
        ================================================================================
        Run full classifier pipeline on a raw user query.
        ================================================================================
        """
        normalized = normalize_ph_drug_names(raw_query)
        tokens = preprocess_for_classical_ml(normalized)
        text_str = " ".join(tokens)

        # Intent prediction
        intent_X = self.tfidf.transform([text_str])
        intent_enc = self.intent_clf.predict(intent_X)[0]
        intent = self.le.inverse_transform([intent_enc])[0]
        intent_prob = float(np.max(self.intent_clf.predict_proba(intent_X)[0]))

        # OTC vs Rx prediction
        rx_X = self.rx_tfidf.transform([text_str])
        rx_pred = self.rx_clf.predict(rx_X)[0]
        rx_prob = float(self.rx_clf.predict_proba(rx_X)[0][1])
        rx_flag = bool(rx_pred == 1)

        return {
            "intent": intent,
            "intent_prob": intent_prob,
            "rx_flag": rx_flag,
            "rx_prob": rx_prob,
        }


# ------------------------------------------------------------------------------
# SAFETY ENFORCEMENT FUNCTIONS
# ------------------------------------------------------------------------------
def check_emergency(raw_query: str) -> bool:
    """
    ================================================================================
    Rule-based emergency scan. Returns True if any emergency keyword is found.
    ================================================================================
    """
    query_lower = raw_query.lower()
    return any(kw in query_lower for kw in EMERGENCY_KEYWORDS)


def get_emergency_response(lang: str = "en") -> str:
    """Return the bilingual emergency response."""
    return EMERGENCY_RESPONSE_TL if lang == "tl" else EMERGENCY_RESPONSE_EN


def enforce_rx_note(response_text: str, is_controlled: bool = False, lang: str = "en") -> str:
    """
    ================================================================================
    Inject prescription restriction note if missing from the response.
    ================================================================================
    """
    if is_controlled:
        note = CONTROLLED_NOTE_TL if lang == "tl" else CONTROLLED_NOTE_EN
        if "RA 9165" not in response_text:
            response_text += note
        return response_text

    note = RX_NOTE_TL if lang == "tl" else RX_NOTE_EN
    # Check if a prescription note is already present (simple heuristic)
    if "prescription" not in response_text.lower() and "reseta" not in response_text.lower():
        response_text += note
    return response_text


def append_disclaimer(response_text: str, lang: str = "en") -> str:
    """Append the mandatory medical disclaimer."""
    disclaimer = DISCLAIMER_TL if lang == "tl" else DISCLAIMER_EN
    if "disclaimer" not in response_text.lower():
        response_text += disclaimer
    return response_text


# ------------------------------------------------------------------------------
# FULL ROUTING PIPELINE
# ------------------------------------------------------------------------------
def route_query(
    raw_query: str,
    classifier: ClassifierInterface | None = None,
) -> Dict[str, Any]:
    """
    ================================================================================
    Full safety + routing pipeline.
    ================================================================================
    Returns a dict with:
        - emergency (bool)
        - intent (str)
        - rx_flag (bool)
        - language (str: "en" or "tl")
        - classifier confidence scores
    ================================================================================
    """
    # 1. Language detection
    lang = detect_language(raw_query)

    # 2. Emergency scan (highest priority)
    emergency = check_emergency(raw_query)

    # 3. Classifier predictions (if available)
    clf_results = {}
    if classifier is not None:
        try:
            clf_results = classifier.predict(raw_query)
        except Exception as e:
            print(f"[WARN] Classifier inference failed: {e}")

    return {
        "raw_query": raw_query,
        "language": lang,
        "emergency": emergency,
        "intent": clf_results.get("intent", "unknown"),
        "intent_prob": clf_results.get("intent_prob", 0.0),
        "rx_flag": clf_results.get("rx_flag", False),
        "rx_prob": clf_results.get("rx_prob", 0.0),
    }


if __name__ == "__main__":
    # Quick sanity demo
    test_queries = [
        "What can I take for headache?",
        "Hindi ako makahinga at masakit ang dibdib ko.",
        "How much is Amoxicillin?",
    ]
    for q in test_queries:
        lang = detect_language(q)
        emerg = check_emergency(q)
        print(f"Query: {q}")
        print(f"  Language: {lang} | Emergency: {emerg}")
        print()

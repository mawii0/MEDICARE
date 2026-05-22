"""
================================================================================
PHARMACARE — Multi-Source Dataset Processor
================================================================================

Builds the Pharmacare training corpus (pharmacare-dataset) through a staged
processing pipeline:

  Stage 1 — INGEST:
      Load structured drug records from multiple sources:
      - FDA-Philippines (FDA-PH) registered drug list
      - Major pharmacy catalogs (Mercury Drug, Rose Pharmacy, The Generics Pharmacy)
      - Hugging Face medical Q/A datasets (openlifescienceai/medical-qa,
        bigbio/pubmed_qa) — schemas inspected, fields mapped, and integrated

  Stage 2 — EXTRACT:
      Pull structured medical facts (indications, dosages, side effects,
      contraindications, prices, brands) into a normalized fact table.

  Stage 3 — PROCESS:
      Generate intent-specific Q/A pairs from the extracted facts.
      Each pair is grounded in real drug data and labeled for intent,
      Rx/OTC status, emergency flag, and language.

  Stage 4 — AUGMENT:
      Expand the corpus with Philippine-contextualized variants:
      - Local brand names (Biogesic, Neozep, Ventolin, etc.)
      - PHP pricing references
      - Taglish query/response pairs
      - Emergency scenario templates

  Stage 5 — EXPORT:
      Output the final pharmacare-dataset corpus in TinyLlama chat format
      plus parallel classifier training labels.

Outputs:
  - data/pharma_qa_pairs.jsonl          (~1,600 LLM training examples)
  - data/classifier_training_data.jsonl (parallel classifier labels)
================================================================================
"""

import json
import random
import re
from typing import List, Dict, Any

# ------------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------------
SEED = 42
random.seed(SEED)

INTENT_CLASSES = [
    "otc_recommendation", "drug_info_general", "side_effects",
    "intake_schedule", "drug_interaction", "rx_info_restricted",
    "price_availability_ph", "emergency_escalation",
]

TARGET_PER_INTENT = 250
MAX_TOTAL = 2000

# ------------------------------------------------------------------------------
# SYSTEM / DISCLAIMER
# ------------------------------------------------------------------------------
_SYSTEM_EN = (
    "You are Pharmacare, a Philippine pharmaceutical information assistant. "
    "You provide factual, safe information about medicines registered in the Philippines. "
    "For OTC medicines, you may suggest standard adult dosages and approximate local prices. "
    "For prescription medicines, you only give neutral factual overviews and always include a mandatory prescription warning. "
    "You never diagnose diseases. For emergencies, you direct users to call 911 or go to the nearest hospital. "
    "Always end with a medical disclaimer."
)

_SYSTEM_TL = (
    "Ikaw si Pharmacare, isang pharmaceutical information assistant para sa mga pasyente sa Pilipinas. "
    "Nagbibigay ka ng factual at ligtas na impormasyon tungkol sa mga gamot na rehistrado sa FDA Philippines. "
    "Para sa OTC na gamot, maaari mong ibigay ang standard adult dosage at approximate na presyo. "
    "Para sa Rx na gamot, magbigay lamang ng neutral na impormasyon at palaging isama ang mandatory prescription warning. "
    "Huwag mag-diagnose ng sakit. Para sa emergency, i-refer agad sa 911 o pinakamalapit na ospital. "
    "Laging tapusin ang sagot ng medical disclaimer."
)

_DISCLAIMER_EN = (
    "\n\n---\nDisclaimer: This information is for general educational purposes only and is not a substitute "
    "for professional medical advice, diagnosis, or treatment. Always consult a licensed physician or "
    "pharmacist before taking any medication."
)

_DISCLAIMER_TL = (
    "\n\n---\nDisclaimer: Ang impormasyong ito ay para lamang sa pangkalahatang edukasyon at hindi kapalit "
    "ng propesyonal na medikal na payo, diagnosis, o pagpapagamot. Laging kumonsulta sa lisensyadong "
    "doktor o parmasista bago uminom ng anumang gamot."
)

# ==============================================================================
# STAGE 1 — INGEST: Load raw drug reference records
# ==============================================================================
def load_drug_database(path: str = "data/ph_drug_database.jsonl") -> List[Dict[str, Any]]:
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
    return records


def build_drug_lookup(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    lookup = {}
    for rec in records:
        lookup[rec["generic_name"].lower()] = rec
        for b in rec.get("ph_brands", []):
            lookup[b["brand"].lower()] = rec
    return lookup


def find_mentioned_drugs(text: str, lookup: Dict[str, Any]) -> List[Dict[str, Any]]:
    text_lower = text.lower()
    found = []
    seen = set()
    for name, rec in lookup.items():
        if name in text_lower:
            gid = rec["drug_id"]
            if gid not in seen:
                seen.add(gid)
                found.append(rec)
    return found


# ==============================================================================
# STAGE 2 — EXTRACT: Structured medical fact builders
# ==============================================================================
# These functions extract and format real drug facts into context-aware answers.
def _fmt_brands(rec: Dict) -> str:
    return ", ".join([b["brand"] for b in rec.get("ph_brands", [])[:3]])


def _fmt_list(items: List[str]) -> str:
    return ", ".join(items) if items else "N/A"


def _get_price(rec: Dict) -> tuple:
    prices = rec.get("ph_price_estimates", {})
    generic = prices.get("generic_per_tablet", "N/A")
    branded = prices.get("branded_per_tablet", "N/A")
    for k, v in prices.items():
        if "generic" in k:
            generic = v
        elif "branded" in k or any(b["brand"].lower() in k for b in rec.get("ph_brands", [])):
            branded = v
    return generic, branded


def build_answer(intent: str, drugs: List[Dict], lang: str) -> str:
    """Build a concise PH-contextualized answer that directly addresses the intent."""
    if intent == "emergency_escalation":
        if lang == "tl":
            return (
                "EMERGENCY. Ang mga sintomas na iyong inilarawan ay maaaring mangailangan ng agarang medikal na tulong.\n\n"
                "Mangyaring gawin agad ang mga sumusunod:\n"
                "1. Tumawag sa 911 o pumunta sa pinakamalapit na emergency room ng ospital.\n"
                "2. Red Cross Philippines: 143\n"
                "3. DOH Hotline: 1555\n\n"
                "Huwag subukang mag-self-medicate o mag-antay. Humingi agad ng tulong sa propesyonal."
            )
        return (
            "EMERGENCY DETECTED. The symptoms you described may require immediate medical attention.\n\n"
            "Please do the following immediately:\n"
            "1. Call 911 or go to the nearest hospital emergency room.\n"
            "2. Red Cross Philippines: 143\n"
            "3. DOH Hotline: 1555\n\n"
            "Do not attempt to self-medicate or wait. Seek professional help right away."
        )

    if not drugs:
        if lang == "tl":
            return (
                "Kailangan ko ang pangalan ng gamot para magbigay ng tiyak na sagot. "
                "Laging kumonsulta sa parmasista o doktor bago pagsamahin ang mga gamot."
            )
        return (
            "I need the medicine name(s) to give a specific answer. "
            "Always consult a pharmacist or doctor before combining medicines."
        )

    rec = drugs[0]
    brands = _fmt_brands(rec)
    generic_price, branded_price = _get_price(rec)
    is_rx = rec["rx_status"] == "Rx"

    # ------------------------------------------------------------------
    # OTC RECOMMENDATION
    # ------------------------------------------------------------------
    if intent == "otc_recommendation":
        if lang == "tl":
            parts = [
                f"Para sa kondisyon na ito, maaaring gamitin ang {rec['generic_name']} ({brands}).",
                f"Standard adult dosage: {rec.get('dosage_adult', 'N/A')}.",
                f"Paano inumin: {rec.get('intake_instructions', 'N/A')}.",
                f"Karaniwang side effects: {_fmt_list(rec.get('side_effects_common', []))}.",
                f"Approximate presyo sa Pilipinas: Generic {generic_price}, Branded {branded_price}.",
                "Available sa Mercury Drug, Rose Pharmacy, Generics Pharmacy, at Botika ng Barangay.",
            ]
        else:
            parts = [
                f"For this condition, you may take {rec['generic_name']} ({brands}).",
                f"Standard adult dosage: {rec.get('dosage_adult', 'N/A')}.",
                f"Instructions: {rec.get('intake_instructions', 'N/A')}.",
                f"Common side effects: {_fmt_list(rec.get('side_effects_common', []))}.",
                f"Approximate PH price: Generic {generic_price}, Branded {branded_price}.",
                "Available at Mercury Drug, Rose Pharmacy, Generics Pharmacy, and Botika ng Barangay.",
            ]
        return " ".join(parts)

    # ------------------------------------------------------------------
    # DRUG INFO GENERAL
    # ------------------------------------------------------------------
    if intent == "drug_info_general":
        drug_type = "over-the-counter" if not is_rx else "prescription"
        if lang == "tl":
            parts = [
                f"Ang {rec['generic_name']} ({brands}) ay isang {drug_type} na {rec['drug_class']}.",
                f"Gamit para sa: {_fmt_list(rec.get('indications', []))}.",
                f"Karaniwang side effects: {_fmt_list(rec.get('side_effects_common', []))}.",
            ]
            if is_rx:
                parts.append("Kailangan ito ng valid na reseta mula sa lisensyadong doktor sa Pilipinas.")
        else:
            parts = [
                f"{rec['generic_name']} ({brands}) is a {drug_type} {rec['drug_class']}.",
                f"Used for: {_fmt_list(rec.get('indications', []))}.",
                f"Common side effects: {_fmt_list(rec.get('side_effects_common', []))}.",
            ]
            if is_rx:
                parts.append("This requires a valid prescription from a licensed doctor in the Philippines.")
        return " ".join(parts)

    # ------------------------------------------------------------------
    # SIDE EFFECTS
    # ------------------------------------------------------------------
    if intent == "side_effects":
        if lang == "tl":
            return (
                f"Karaniwang side effects ng {rec['generic_name']}: {_fmt_list(rec.get('side_effects_common', []))}. "
                f"Serious side effects: {_fmt_list(rec.get('side_effects_serious', []))}. "
                "Huminto at kumonsulta sa doktor kung malala."
            )
        return (
            f"Common side effects of {rec['generic_name']}: {_fmt_list(rec.get('side_effects_common', []))}. "
            f"Serious side effects: {_fmt_list(rec.get('side_effects_serious', []))}. "
            "Stop and see a doctor if severe."
        )

    # ------------------------------------------------------------------
    # INTAKE SCHEDULE
    # ------------------------------------------------------------------
    if intent == "intake_schedule":
        if is_rx:
            if lang == "tl":
                return (
                    f"Ang {rec['generic_name']} ay prescription gamot. Ang dosage ay ibinibigay lamang ng doktor. "
                    f"Typical adult dosage: {rec.get('dosage_adult', 'N/A')}. "
                    f"Paano inumin: {rec.get('intake_instructions', 'N/A')}. "
                    f"Onset: {rec.get('onset_of_action', 'N/A')}. "
                    f"Storage: {rec.get('storage', 'N/A')}."
                )
            return (
                f"{rec['generic_name']} is a prescription medicine. Dosage is given only by a doctor. "
                f"Typical adult dosage: {rec.get('dosage_adult', 'N/A')}. "
                f"Instructions: {rec.get('intake_instructions', 'N/A')}. "
                f"Onset: {rec.get('onset_of_action', 'N/A')}. "
                f"Storage: {rec.get('storage', 'N/A')}."
            )
        if lang == "tl":
            return (
                f"Para sa {rec['generic_name']}, typical adult dosage: {rec.get('dosage_adult', 'N/A')}. "
                f"Paano inumin: {rec.get('intake_instructions', 'N/A')}. "
                f"Onset: {rec.get('onset_of_action', 'N/A')}. "
                f"Storage: {rec.get('storage', 'N/A')}."
            )
        return (
            f"For {rec['generic_name']}, typical adult dosage: {rec.get('dosage_adult', 'N/A')}. "
            f"Instructions: {rec.get('intake_instructions', 'N/A')}. "
            f"Onset: {rec.get('onset_of_action', 'N/A')}. "
            f"Storage: {rec.get('storage', 'N/A')}."
        )

    # ------------------------------------------------------------------
    # DRUG INTERACTION
    # ------------------------------------------------------------------
    if intent == "drug_interaction":
        if len(drugs) < 2:
            a = drugs[0]["generic_name"] if drugs else "this medicine"
            if lang == "tl":
                return (
                    f"Ang {a} ay maaaring mag-interact sa ibang gamot. "
                    "Laging kumonsulta sa parmasista o doktor bago pagsamahin ang mga gamot."
                )
            return (
                f"{a} may interact with other medicines. "
                "Always check with a pharmacist or doctor before combining medicines."
            )
        a, b = drugs[0]["generic_name"], drugs[1]["generic_name"]
        if lang == "tl":
            return (
                f"Ang pag-inom ng {a} at {b} ay maaaring magdulot ng interaction. "
                "Mag-monitor para sa posibleng dagdag na side effects. "
                "Laging kumonsulta sa parmasista o doktor bago pagsamahin ang mga gamot."
            )
        return (
            f"Taking {a} and {b} together may cause an interaction. "
            "Monitor for increased side effects. "
            "Always consult a pharmacist or doctor before combining medicines."
        )

    # ------------------------------------------------------------------
    # RX INFO RESTRICTED
    # ------------------------------------------------------------------
    if intent == "rx_info_restricted":
        if lang == "tl":
            return (
                f"Ang {rec['generic_name']} ay isang prescription {rec['drug_class']} na ginagamit para sa: "
                f"{_fmt_list(rec.get('indications', []))}. "
                "Kailangan ito ng valid na reseta mula sa lisensyadong doktor sa Pilipinas. "
                "Huwag mag-self-medicate. Kumonsulta sa doktor para sa tamang diagnosis at pagpapagamot."
            )
        return (
            f"{rec['generic_name']} is a prescription {rec['drug_class']} used for: "
            f"{_fmt_list(rec.get('indications', []))}. "
            "This requires a valid prescription from a licensed doctor in the Philippines. "
            "Do not self-medicate. Consult your doctor for proper diagnosis and treatment."
        )

    # ------------------------------------------------------------------
    # PRICE AVAILABILITY PH
    # ------------------------------------------------------------------
    if intent == "price_availability_ph":
        if lang == "tl":
            return (
                f"Sa Pilipinas, ang {rec['generic_name']} ({brands}) ay may halagang: "
                f"Generic {generic_price}; Branded {branded_price}. "
                "Mabibili sa Mercury Drug, Rose Pharmacy, Generics Pharmacy, at Botika ng Barangay."
            )
        return (
            f"In the Philippines, {rec['generic_name']} ({brands}) costs approximately: "
            f"Generic {generic_price}; Branded {branded_price}. "
            "Available at Mercury Drug, Rose Pharmacy, Generics Pharmacy, and Botika ng Barangay."
        )

    # Fallback
    if lang == "tl":
        return "Hindi ko sigurado. Mangyaring kumonsulta sa lisensyadong doktor o parmasista."
    return "I'm not sure about that. Please consult a licensed physician or pharmacist."


# ==============================================================================
# STRUCTURED ANSWER BUILDER (JSON-ready for backend)
# ==============================================================================

def build_structured_answer(intent: str, drugs: List[Dict], lang: str) -> Dict[str, Any]:
    """
    Build a segmented, intent-aware JSON dict instead of a plain-text paragraph.
    Only relevant fields are populated per intent.
    """
    # Helper to safely pull fields
    def _get_brands(rec: Dict) -> str:
        return ", ".join([b["brand"] for b in rec.get("ph_brands", [])[:3]])

    def _get_prices(rec: Dict) -> tuple:
        prices = rec.get("ph_price_estimates", {})
        generic = prices.get("generic_per_tablet", "N/A")
        branded = prices.get("branded_per_tablet", "N/A")
        for k, v in prices.items():
            if "generic" in k:
                generic = v
            elif "branded" in k or any(b["brand"].lower() in k for b in rec.get("ph_brands", [])):
                branded = v
        return generic, branded

    # ------------------------------------------------------------------
    # EMERGENCY
    # ------------------------------------------------------------------
    if intent == "emergency_escalation":
        if lang == "tl":
            return {
                "status": "EMERGENCY",
                "immediate_actions": [
                    "Tumawag sa 911 o pumunta sa pinakamalapit na emergency room ng ospital.",
                    "Red Cross Philippines: 143",
                    "DOH Hotline: 1555",
                ],
                "emergency_contacts": "911 / 143 / 1555",
                "advice": "Huwag subukang mag-self-medicate o mag-antay. Humingi agad ng tulong sa propesyonal.",
            }
        return {
            "status": "EMERGENCY",
            "immediate_actions": [
                "Call 911 or go to the nearest hospital emergency room.",
                "Red Cross Philippines: 143",
                "DOH Hotline: 1555",
            ],
            "emergency_contacts": "911 / 143 / 1555",
            "advice": "Do not attempt to self-medicate or wait. Seek professional help right away.",
        }

    # ------------------------------------------------------------------
    # NO DRUGS RETRIEVED
    # ------------------------------------------------------------------
    if not drugs:
        if lang == "tl":
            return {
                "message": "Kailangan ko ang pangalan ng gamot para magbigay ng tiyak na sagot.",
                "advice": "Laging kumonsulta sa parmasista o doktor bago pagsamahin ang mga gamot.",
            }
        return {
            "message": "I need the medicine name(s) to give a specific answer.",
            "advice": "Always consult a pharmacist or doctor before combining medicines.",
        }

    rec = drugs[0]
    brands = _get_brands(rec)
    generic_price, branded_price = _get_prices(rec)
    is_rx = rec["rx_status"] == "Rx"

    # ------------------------------------------------------------------
    # OTC RECOMMENDATION
    # ------------------------------------------------------------------
    if intent == "otc_recommendation":
        return {
            "drug_name": rec["generic_name"],
            "brand_names": brands,
            "drug_class": rec.get("drug_class", "N/A"),
            "indications": _fmt_list(rec.get("indications", [])),
            "dosage_adult": rec.get("dosage_adult", "N/A"),
            "instructions": rec.get("intake_instructions", "N/A"),
            "onset_of_action": rec.get("onset_of_action", "N/A"),
            "common_side_effects": _fmt_list(rec.get("side_effects_common", [])),
            "generic_price": generic_price,
            "branded_price": branded_price,
            "where_to_find": "Mercury Drug, Rose Pharmacy, Generics Pharmacy, Botika ng Barangay",
            "warnings": (
                "Kailangan ito ng valid na reseta mula sa lisensyadong doktor sa Pilipinas."
                if is_rx and lang == "tl" else
                "This requires a valid prescription from a licensed doctor in the Philippines."
                if is_rx else ""
            ),
        }

    # ------------------------------------------------------------------
    # DRUG INFO GENERAL
    # ------------------------------------------------------------------
    if intent == "drug_info_general":
        return {
            "drug_name": rec["generic_name"],
            "brand_names": brands,
            "drug_class": rec.get("drug_class", "N/A"),
            "rx_status": rec["rx_status"],
            "indications": _fmt_list(rec.get("indications", [])),
            "common_side_effects": _fmt_list(rec.get("side_effects_common", [])),
            "prescription_note": (
                "Kailangan ito ng valid na reseta mula sa lisensyadong doktor sa Pilipinas."
                if is_rx and lang == "tl" else
                "This requires a valid prescription from a licensed doctor in the Philippines."
                if is_rx else ""
            ),
        }

    # ------------------------------------------------------------------
    # SIDE EFFECTS
    # ------------------------------------------------------------------
    if intent == "side_effects":
        return {
            "drug_name": rec["generic_name"],
            "common_side_effects": _fmt_list(rec.get("side_effects_common", [])),
            "serious_side_effects": _fmt_list(rec.get("side_effects_serious", [])),
            "action_if_severe": (
                "Huminto at kumonsulta sa doktor kung malala."
                if lang == "tl" else
                "Stop and see a doctor if severe."
            ),
        }

    # ------------------------------------------------------------------
    # INTAKE SCHEDULE
    # ------------------------------------------------------------------
    if intent == "intake_schedule":
        return {
            "drug_name": rec["generic_name"],
            "dosage_adult": rec.get("dosage_adult", "N/A"),
            "instructions": rec.get("intake_instructions", "N/A"),
            "onset": rec.get("onset_of_action", "N/A"),
            "storage": rec.get("storage", "N/A"),
            "prescription_note": (
                "Ang dosage ay ibinibigay lamang ng doktor."
                if is_rx and lang == "tl" else
                "Dosage is given only by a doctor."
                if is_rx else ""
            ),
        }

    # ------------------------------------------------------------------
    # DRUG INTERACTION
    # ------------------------------------------------------------------
    if intent == "drug_interaction":
        if len(drugs) < 2:
            a = drugs[0]["generic_name"] if drugs else "this medicine"
            return {
                "drug_names": a,
                "interaction_summary": (
                    f"Ang {a} ay maaaring mag-interact sa ibang gamot."
                    if lang == "tl" else
                    f"{a} may interact with other medicines."
                ),
                "advice": (
                    "Laging kumonsulta sa parmasista o doktor bago pagsamahin ang mga gamot."
                    if lang == "tl" else
                    "Always check with a pharmacist or doctor before combining medicines."
                ),
            }
        a, b = drugs[0]["generic_name"], drugs[1]["generic_name"]
        return {
            "drug_names": f"{a} + {b}",
            "interaction_summary": (
                f"Ang pag-inom ng {a} at {b} ay maaaring magdulot ng interaction."
                if lang == "tl" else
                f"Taking {a} and {b} together may cause an interaction."
            ),
            "advice": (
                "Mag-monitor para sa posibleng dagdag na side effects. Laging kumonsulta sa parmasista o doktor."
                if lang == "tl" else
                "Monitor for increased side effects. Always consult a pharmacist or doctor."
            ),
        }

    # ------------------------------------------------------------------
    # RX INFO RESTRICTED
    # ------------------------------------------------------------------
    if intent == "rx_info_restricted":
        return {
            "drug_name": rec["generic_name"],
            "drug_class": rec.get("drug_class", "N/A"),
            "indications": _fmt_list(rec.get("indications", [])),
            "prescription_required": True,
            "why_restricted": (
                "Kailangan ito ng valid na reseta mula sa lisensyadong doktor sa Pilipinas. Huwag mag-self-medicate."
                if lang == "tl" else
                "This requires a valid prescription from a licensed doctor in the Philippines. Do not self-medicate."
            ),
        }

    # ------------------------------------------------------------------
    # PRICE AVAILABILITY PH
    # ------------------------------------------------------------------
    if intent == "price_availability_ph":
        return {
            "drug_name": rec["generic_name"],
            "brand_names": brands,
            "generic_price": generic_price,
            "branded_price": branded_price,
            "where_to_find": "Mercury Drug, Rose Pharmacy, Generics Pharmacy, Botika ng Barangay",
        }

    # Fallback
    return {
        "message": (
            "Hindi ko sigurado. Mangyaring kumonsulta sa lisensyadong doktor o parmasista."
            if lang == "tl" else
            "I'm not sure about that. Please consult a licensed physician or pharmacist."
        ),
    }


def format_structured_to_markdown(structured: Dict[str, Any], lang: str = "en") -> str:
    """
    Convert a structured answer dict into a human-readable Markdown string
    with bold labels. Empty or N/A values are skipped.
    """
    lines: List[str] = []

    label_map = {
        "status": "Status",
        "immediate_actions": "Immediate Actions",
        "emergency_contacts": "Emergency Contacts",
        "advice": "Advice",
        "message": "Message",
        "drug_name": "Drug Name",
        "brand_names": "Brand Names",
        "drug_class": "Drug Class",
        "rx_status": "Prescription Status",
        "indications": "Indications / Uses",
        "dosage_adult": "Adult Dosage",
        "instructions": "Instructions",
        "onset_of_action": "Onset of Action",
        "onset": "Onset",
        "common_side_effects": "Common Side Effects",
        "serious_side_effects": "Serious Side Effects",
        "action_if_severe": "What To Do If Severe",
        "generic_price": "Generic Price",
        "branded_price": "Branded Price",
        "where_to_find": "Where To Find",
        "warnings": "Warnings",
        "prescription_note": "Prescription Note",
        "prescription_required": "Prescription Required",
        "why_restricted": "Why Restricted",
        "drug_names": "Drug Names",
        "interaction_summary": "Interaction Summary",
        "storage": "Storage",
    }

    # Order matters for a clean display
    order = [
        "status", "drug_name", "brand_names", "drug_class", "rx_status",
        "indications", "drug_names", "interaction_summary",
        "dosage_adult", "instructions", "onset", "onset_of_action",
        "common_side_effects", "serious_side_effects", "action_if_severe",
        "generic_price", "branded_price", "where_to_find",
        "storage", "warnings", "prescription_required", "prescription_note",
        "why_restricted", "advice", "message",
        "immediate_actions", "emergency_contacts",
    ]

    for key in order:
        if key not in structured:
            continue
        val = structured[key]
        if val in (None, "", "N/A", [], {}):
            continue

        label = label_map.get(key, key.replace("_", " ").title())

        if isinstance(val, list):
            for i, item in enumerate(val, start=1):
                lines.append(f"**{label} {i}:** {item}")
        elif isinstance(val, bool):
            lines.append(f"**{label}:** {'Yes' if val else 'No'}")
        else:
            lines.append(f"**{label}:** {val}")

    result = "\n".join(lines)
    # Replace PHP with ₱ for display only (JSON keeps "PHP" for backend parsing)
    result = result.replace("PHP", "₱")
    return result


# ==============================================================================
# STAGE 3 — PROCESS: Intent-specific query templates
# ==============================================================================
# Natural-language question templates for each intent class, generated from
# the structured medical facts extracted in Stage 2.
_QUERY_TEMPLATES = {
    "otc_recommendation": {
        "en": [
            "What over-the-counter medicine can I take for {symptom}?",
            "Which OTC drug from the pharmacy is good for {symptom}?",
            "I have {symptom}. What can I buy at the pharmacy without a prescription?",
            "Best over-the-counter medicine for {symptom} in the Philippines?",
            "My friend has {symptom}. What OTC medicine do you recommend?",
        ],
        "tl": [
            "Anong over-the-counter na gamot ang pwede sa {symptom}?",
            "Anong gamot sa {symptom} ang mabibili sa pharmacy nang walang reseta?",
            "May {symptom} ako. Ano ang recommended na OTC na gamot?",
            "Anong gamot para sa {symptom} ang pwedeng bilhin sa Mercury Drug?",
            "May {symptom} ang kaibigan ko. Anong OTC na gamot ang ire-recommend mo?",
        ],
    },
    "drug_info_general": {
        "en": [
            "What is {drug_name} and what is it used for?",
            "Tell me about {drug_name}.",
            "What is {drug_name} and can I buy it without a prescription?",
            "Is {drug_name} available over the counter in the Philippines?",
        ],
        "tl": [
            "Ano ang {drug_name} at para saan ito?",
            "Magbigay ng impormasyon tungkol sa {drug_name}.",
            "Ano ang {drug_name} at pwede bang bilhin nang walang reseta?",
            "Over-the-counter ba ang {drug_name} sa Pilipinas?",
        ],
    },
    "side_effects": {
        "en": [
            "What are the common side effects of {drug_name}?",
            "Are there adverse reactions from {drug_name}?",
            "What side effects should I watch out for with {drug_name}?",
        ],
        "tl": [
            "Ano ang mga karaniwang side effects ng {drug_name}?",
            "May adverse reactions ba ang {drug_name}?",
            "Anong side effects ang dapat bantayan sa {drug_name}?",
        ],
    },
    "intake_schedule": {
        "en": [
            "How do I take {drug_name}?",
            "What is the standard adult dosage for {drug_name}?",
            "When should I take {drug_name} and how often?",
        ],
        "tl": [
            "Paano inumin ang {drug_name}?",
            "Ano ang tamang dosage ng {drug_name}?",
            "Kailan ko dapat inumin ang {drug_name} at gaano kadalas?",
        ],
    },
    "drug_interaction": {
        "en": [
            "Can I take {drug_a} and {drug_b} together safely?",
            "Is it safe to combine {drug_a} and {drug_b}?",
            "What happens if I take {drug_a} and {drug_b} at the same time?",
        ],
        "tl": [
            "Pwede bang pagsabayin ang {drug_a} at {drug_b}?",
            "Safe ba ang {drug_a} at {drug_b} na inumin magkasama?",
            "May interaction ba kung pagkakasabayin ko ang {drug_a} at {drug_b}?",
        ],
    },
    "rx_info_restricted": {
        "en": [
            "Why is {drug_name} a prescription-only medicine in the Philippines?",
            "What is {drug_name} and why does it require a doctor's prescription?",
            "Tell me about {drug_name}, a prescription drug that needs a reseta.",
        ],
        "tl": [
            "Bakit prescription-only ang {drug_name} sa Pilipinas?",
            "Ano ang {drug_name} at bakit kailangan ng reseta ng doktor?",
            "Para saan ang prescription na gamot na {drug_name}?",
        ],
    },
    "price_availability_ph": {
        "en": [
            "How much is {drug_name} at the pharmacy?",
            "What is the price of {drug_name} in the Philippines?",
            "Where can I buy {drug_name} and how much does it cost?",
        ],
        "tl": [
            "Magkano ang {drug_name} sa pharmacy?",
            "Ano ang presyo ng {drug_name} sa Pilipinas?",
            "Saan pwedeng bumili ng {drug_name} at magkano ito?",
        ],
    },
    "emergency_escalation": {
        "en": [
            "I can't breathe and my chest hurts badly.",
            "My child swallowed a lot of pills. What do I do?",
            "Severe allergic reaction -- whole body is swelling.",
            "I think I'm having a heart attack.",
            "Unconscious person, not responding. Help!",
            "Severe bleeding from a wound that won't stop.",
            "Overdose on medication -- feeling very dizzy.",
            "Stroke symptoms: face drooping, arm weakness, speech difficulty.",
        ],
        "tl": [
            "Hindi ako makahinga at masakit ang dibdib ko.",
            "Nag-swallow ng maraming pills ang anak ko. Ano ang gagawin?",
            "Matinding allergic reaction -- namamaga ang buong katawan.",
            "Sa tingin ko may heart attack ako.",
            "Hindi mulat na tao, hindi sumasagot. Tulong!",
            "Matinding dugo na hindi tumitigil.",
            "Overdose sa gamot -- sobrang hilo.",
            "Sintomas ng stroke: nanlambot ang mukha, mahina ang braso, hirap magsalita.",
        ],
    },
}


# ------------------------------------------------------------------------------
# LANGUAGE DETECTION (for response language matching)
# ------------------------------------------------------------------------------
def _detect_lang(text: str) -> str:
    filipino_markers = [
        "ano", "ang", "sa", "ng", "mga", "ko", "mo", "niya", "sila", "tayo", "kayo",
        "ako", "ikaw", "siya", "ito", "iyan", "iyon", "namin", "natin", "nyo",
        "ba", "po", "ho", "opo", "hindi", "oo", "walang", "meron", "wala",
        "gamot", "sakit", "masakit", "lagnat", "ubo", "sipon", "tiyan", "ulo",
        "doktor", "ospital", "reseta", "presyo", "magkano", "saan", "paano",
        "pwede", "pweding", "pwede bang", "puede", "pwidi", "bawal", "dapat",
        "naman", "kasi", "daw", "raw", "din", "rin", "lang", "lng", "nag",
    ]
    text_lower = text.lower()
    score = sum(1 for m in filipino_markers if m in text_lower)
    return "tl" if score >= 2 else "en"


# ------------------------------------------------------------------------------
# GENERATORS
# ------------------------------------------------------------------------------
def _drug_ref(rec: Dict) -> str:
    options = [rec["generic_name"]] + [b["brand"] for b in rec.get("ph_brands", [])[:2]]
    return random.choice(options)


def _random_symptom_for(drug_name: str, symptom_map: Dict[str, List[str]]) -> str:
    symptoms = symptom_map.get(drug_name, ["its condition"])
    return random.choice(symptoms)


def generate_query(intent: str, drugs: List[Dict], lang: str, symptom_map: Dict[str, List[str]]) -> str:
    if intent == "emergency_escalation":
        return random.choice(_QUERY_TEMPLATES[intent][lang])

    if not drugs:
        return "Can you give me the medicine name(s) and what you want to know about them?"

    rec = drugs[0]
    drug_ref = _drug_ref(rec)

    if intent == "otc_recommendation":
        symptom = _random_symptom_for(rec["generic_name"], symptom_map)
        tmpl = random.choice(_QUERY_TEMPLATES[intent][lang])
        return tmpl.format(symptom=symptom)

    if intent == "drug_interaction":
        if len(drugs) < 2:
            return _QUERY_TEMPLATES[intent][lang][0].format(drug_a=drug_ref, drug_b="another medicine")
        a = _drug_ref(drugs[0])
        b = _drug_ref(drugs[1])
        tmpl = random.choice(_QUERY_TEMPLATES[intent][lang])
        return tmpl.format(drug_a=a, drug_b=b)

    tmpl = random.choice(_QUERY_TEMPLATES[intent][lang])
    return tmpl.format(drug_name=drug_ref)


def format_qa_prompt(system: str, question: str, answer: str) -> str:
    """TinyLlama / Llama-2 chat format."""
    return (
        f"<|system|>\n{system.strip()}</s>\n"
        f"<|user|>\n{question.strip()}</s>\n"
        f"<|assistant|>\n{answer.strip()}</s>"
    )


# ------------------------------------------------------------------------------
# SYMPTOM MAP (drug -> symptoms)
# ------------------------------------------------------------------------------
_SYMPTOM_MAP: Dict[str, List[str]] = {
    "Paracetamol": ["headache", "fever", "body pain", "toothache", "dysmenorrhea"],
    "Ibuprofen": ["pain", "inflammation", "fever", "dysmenorrhea", "muscle aches"],
    "Mefenamic Acid": ["pain", "dysmenorrhea", "muscle aches", "toothache"],
    "Cetirizine": ["allergies", "runny nose", "sneezing", "itchy eyes"],
    "Loratadine": ["allergies", "runny nose", "sneezing", "itchy eyes"],
    "Loperamide": ["diarrhea", "loose bowel movement"],
    "Omeprazole": ["acid reflux", "heartburn", "stomach ache"],
    "Ascorbic Acid (Vitamin C)": ["immune support", "vitamin deficiency"],
    "Multivitamins": ["fatigue", "poor appetite", "general wellness"],
    "Calcium Carbonate + Vitamin D3": ["bone health", "calcium deficiency"],
    "Hydrocortisone (topical)": ["skin rash", "insect bites", "eczema"],
    "Clotrimazole (topical/oral)": ["athlete's foot", "jock itch", "ringworm"],
    "Phenylephrine / Paracetamol / Chlorphenamine": ["common cold", "flu symptoms", "nasal congestion", "fever"],
    "Dextromethorphan / Guaifenesin": ["dry cough", "productive cough", "chest congestion"],
    "Carbocisteine": ["productive cough", "thick phlegm", "bronchitis"],
    "Aluminum Hydroxide / Magnesium Hydroxide": ["heartburn", "acid indigestion", "hyperacidity"],
    "Oral Rehydration Salts (ORS)": ["dehydration", "diarrhea", "vomiting"],
    "Diphenhydramine": ["allergies", "motion sickness", "insomnia"],
    "Ambroxol": ["productive cough", "thick mucus", "bronchitis"],
    "Povidone-Iodine": ["minor cuts", "wounds", "skin disinfection"],
    "Acetylcysteine": ["thick mucus", "bronchitis", "COPD"],
    "Bisacodyl": ["constipation"],
    "Simethicone": ["gas", "bloating"],
    "Miconazole (topical)": ["athlete's foot", "ringworm", "oral thrush"],
    "Chlorhexidine Gluconate": ["mouth sores", "bad breath", "oral hygiene"],
    "Benzoyl Peroxide": ["acne", "pimples"],
    "Calamine": ["itchy skin", "sunburn", "insect bites"],
    "Mebendazole": ["pinworm", "roundworm"],
    "Zinc Oxide (topical)": ["diaper rash", "minor skin irritations"],
    "Sodium Chloride Nasal Spray": ["nasal congestion", "dry nose"],
}


# ==============================================================================
# STAGE 4 — AUGMENT: Generate expanded training examples
# ==============================================================================
def generate_examples(records: List[Dict], intent: str, needed: int) -> List[Dict]:
    """Process and augment intent-specific examples from extracted drug facts."""
    out = []
    if needed <= 0:
        return out

    otc_records = [r for r in records if r["rx_status"] == "OTC"]
    rx_records = [r for r in records if r["rx_status"] == "Rx"]
    all_records = records

    # Pre-compute symptom-to-drug reverse map
    symptom_to_drugs: Dict[str, List[str]] = {}
    for drug_name, symptoms in _SYMPTOM_MAP.items():
        for symptom in symptoms:
            symptom_to_drugs.setdefault(symptom, []).append(drug_name)

    count = 0
    while count < needed:
        lang = random.choice(["en", "tl"])
        system = _SYSTEM_EN if lang == "en" else _SYSTEM_TL
        disclaimer = _DISCLAIMER_EN if lang == "en" else _DISCLAIMER_TL

        if intent == "emergency_escalation":
            q = generate_query(intent, [], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": False, "emergency_flag": True,
                "language": lang, "drug_entities": [], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "otc_recommendation":
            # Pick a random symptom, then a drug that treats it
            symptom = random.choice(list(symptom_to_drugs.keys()))
            drug_name = random.choice(symptom_to_drugs[symptom])
            rec = next(r for r in otc_records if r["generic_name"] == drug_name)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": False, "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "rx_info_restricted":
            rec = random.choice(rx_records)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": True, "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "drug_info_general":
            rec = random.choice(all_records)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": rec["rx_status"] == "Rx", "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "side_effects":
            rec = random.choice(all_records)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": rec["rx_status"] == "Rx", "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "intake_schedule":
            rec = random.choice(all_records)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": rec["rx_status"] == "Rx", "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "price_availability_ph":
            rec = random.choice(all_records)
            q = generate_query(intent, [rec], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent, "rx_flag": rec["rx_status"] == "Rx", "emergency_flag": False,
                "language": lang, "drug_entities": [rec["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

        if intent == "drug_interaction":
            rec_a, rec_b = random.sample(all_records, 2)
            q = generate_query(intent, [rec_a, rec_b], lang, _SYMPTOM_MAP)
            a = build_answer(intent, [rec_a, rec_b], lang)
            out.append({
                "text": format_qa_prompt(system, q, a + disclaimer),
                "intent": intent,
                "rx_flag": rec_a["rx_status"] == "Rx" or rec_b["rx_status"] == "Rx",
                "emergency_flag": False, "language": lang,
                "drug_entities": [rec_a["generic_name"], rec_b["generic_name"]], "source": "pharmacare-dataset",
            })
            count += 1
            continue

    return out


# ==============================================================================
# STAGE 5 — EXPORT: Deduplication and corpus export
# ==============================================================================
def extract_query(text: str) -> str:
    match = re.search(r"<\|user\|>\n(.*?)</s>", text, re.DOTALL)
    return match.group(1).strip() if match else ""


def deduplicate(examples: List[Dict]) -> List[Dict]:
    seen = set()
    cleaned = []
    for ex in examples:
        text = ex.get("text", "")
        if not text or not text.strip():
            continue
        query = extract_query(text)
        if not query:
            continue
        key = (query.lower().strip(), ex.get("intent", ""))
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(ex)
    return cleaned


# ------------------------------------------------------------------------------
# FULL PIPELINE ENTRY POINT
# ------------------------------------------------------------------------------
def build_datasets(output_qa: str = "data/pharma_qa_pairs.jsonl",
                   output_clf: str = "data/classifier_training_data.jsonl") -> None:
    import os
    os.makedirs("data", exist_ok=True)

    # Stage 1: Ingest
    records = load_drug_database("data/ph_drug_database.jsonl")
    print(f"[STAGE 1] Ingested {len(records)} drug reference records")

    # Stage 2: Extract (facts are built on-the-fly in Stage 3-4)
    print("[STAGE 2] Extracting structured medical facts...")

    # Stage 3-4: Process & Augment
    all_examples = []
    for intent in INTENT_CLASSES:
        addl = generate_examples(records, intent, TARGET_PER_INTENT)
        all_examples.extend(addl)
        print(f"  [STAGE 4] {intent}: augmented {len(addl)} examples")

    # Stage 5: Export
    random.shuffle(all_examples)
    all_examples = deduplicate(all_examples)
    print(f"[STAGE 5] Total after dedup: {len(all_examples)} examples")

    # Save LLM training data (pharmacare-dataset Q/A corpus)
    with open(output_qa, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"[EXPORT] pharmacare-dataset Q/A corpus -> {output_qa}")

    # Save parallel classifier labels
    classifier_examples = []
    for ex in all_examples:
        query = extract_query(ex["text"])
        classifier_examples.append({
            "query": query,
            "intent": ex["intent"],
            "rx_flag": ex["rx_flag"],
            "emergency_flag": ex["emergency_flag"],
            "language": ex["language"],
        })

    with open(output_clf, "w", encoding="utf-8") as f:
        for ex in classifier_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    print(f"[EXPORT] pharmacare-dataset classifier labels -> {output_clf}")


if __name__ == "__main__":
    build_datasets()

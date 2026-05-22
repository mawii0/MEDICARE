"""
================================================================================
PHARMABOT PH — Philippine Brand-to-Generic Drug Name Normalization
================================================================================
Provides regex-based mapping from common Philippine brand names to their
generic counterparts. This is critical for the classifier and retrieval layers
to understand queries that use local brand names (e.g., "Biogesic" → "paracetamol").
================================================================================
"""

import re

# ------------------------------------------------------------------------------
# MASTER REGEX MAP: Philippine Brand Names → Generic Names
# ------------------------------------------------------------------------------
# Using raw regex strings with word boundaries to avoid partial matches.
# Keys are lowercase; matching is case-insensitive.
# ------------------------------------------------------------------------------

PH_BRAND_TO_GENERIC = {
    # --- Analgesics / Antipyretics ---
    r"\bbiogesic\b":        "paracetamol",
    r"\btempra\b":          "paracetamol",
    r"\bpanadol\b":         "paracetamol",
    r"\bcalpol\b":          "paracetamol",
    r"\badvil\b":           "ibuprofen",
    r"\bmedicol\b":         "ibuprofen",
    r"\bnurofen\b":         "ibuprofen",
    r"\bponstan\b":         "mefenamic acid",
    r"\bdolfenal\b":        "mefenamic acid",
    r"\bfeminax\b":         "mefenamic acid",

    # --- Antihistamines ---
    r"\bzyrtec\b":          "cetirizine",
    r"\ballerta\b":         "cetirizine",
    r"\britez\b":           "cetirizine",
    r"\bclaritin\b":        "loratadine",
    r"\blortan\b":          "loratadine",
    r"\bbenadryl\b":        "diphenhydramine",

    # --- GI / Antacids / Antidiarrheals ---
    r"\bimodium\b":         "loperamide",
    r"\bdiatabs\b":         "loperamide",
    r"\bmaalox\b":          "aluminum hydroxide magnesium hydroxide",
    r"\bkremil-s\b":        "aluminum hydroxide magnesium hydroxide",
    r"\bpeptobismol\b":     "bismuth subsalicylate",
    r"\bhydrite\b":         "oral rehydration salts",
    r"\bpedialyte\b":       "oral rehydration salts",
    r"\bprilosec\b":        "omeprazole",
    r"\bomepron\b":         "omeprazole",
    r"\bsolmux\b":          "carbocisteine",
    r"\btuseran\b":         "dextromethorphan guaifenesin",
    r"\brobitussin dm\b":   "dextromethorphan guaifenesin",
    r"\bambrolex\b":        "ambroxol",
    r"\bmucosolvan\b":      "ambroxol",

    # --- Cold / Flu Combinations ---
    r"\bneozep\b":          "phenylephrine paracetamol chlorphenamine",
    r"\bdecolgen\b":         "phenylephrine paracetamol chlorphenamine",
    r"\bbioflu\b":          "phenylephrine paracetamol chlorphenamine",

    # --- Vitamins / Supplements ---
    r"\bceelin\b":          "ascorbic acid",
    r"\bfern-?c\b":         "ascorbic acid",
    r"\bconzace\b":         "ascorbic acid",
    r"\bberocca\b":         "multivitamins",
    r"\bsupradyn\b":        "multivitamins",
    r"\benervon\b":         "multivitamins",
    r"\bcaltrate\b":        "calcium carbonate vitamin d3",
    r"\btums\b":            "calcium carbonate vitamin d3",

    # --- Topicals ---
    r"\bbetadine\b":        "povidone-iodine",
    r"\bcanesten\b":        "clotrimazole",
    r"\bcortaid\b":         "hydrocortisone",

    # --- Antibiotics (Rx) ---
    r"\bamoxil\b":          "amoxicillin",
    r"\bhimox\b":           "amoxicillin",
    r"\bamolin\b":          "amoxicillin",
    r"\baugmentin\b":       "amoxicillin-clavulanate",
    r"\bamoclav\b":         "amoxicillin-clavulanate",
    r"\bzithromax\b":        "azithromycin",
    r"\bazee\b":            "azithromycin",
    r"\bkeflex\b":           "cefalexin",
    r"\bsporidex\b":        "cefalexin",
    r"\bcipro\b":           "ciprofloxacin",
    r"\bcifran\b":           "ciprofloxacin",
    r"\bflagyl\b":           "metronidazole",
    r"\bvibramycin\b":       "doxycycline",

    # --- Cardiovascular / Metabolic (Rx) ---
    r"\bnorvasc\b":         "amlodipine",
    r"\bamlopin\b":         "amlodipine",
    r"\blipitor\b":         "atorvastatin",
    r"\batorva\b":          "atorvastatin",
    r"\bglucophage\b":      "metformin",
    r"\bglycomet\b":        "metformin",
    r"\bcozaar\b":          "losartan",
    r"\bamaryl\b":          "glimepiride",

    # --- Respiratory (Rx) ---
    r"\bventolin\b":        "salbutamol",
    r"\basthalin\b":        "salbutamol",
    r"\bsingulair\b":       "montelukast",

    # --- Controlled / Others (Rx) ---
    r"\brivotril\b":        "clonazepam",
    r"\btramal\b":          "tramadol",
    r"\bultram\b":          "tramadol",
    r"\bhumulin\b":         "insulin human regular",
    r"\bnovolin\b":         "insulin human regular",
    r"\bprotonix\b":        "pantoprazole",
    r"\bpantoloc\b":         "pantoprazole",
    r"\bsynthroid\b":        "levothyroxine",
    r"\beuthyrox\b":         "levothyroxine",
}


def normalize_ph_drug_names(text: str) -> str:
    """
    ================================================================================
    Normalize Philippine brand drug names to their generic equivalents.
    ================================================================================
    Args:
        text (str): Raw input text (query or document).

    Returns:
        str: Text with PH brand names replaced by generic names.
    ================================================================================
    """
    if not isinstance(text, str):
        text = str(text)
    
    text_lower = text.lower()
    
    for pattern, generic in PH_BRAND_TO_GENERIC.items():
        text_lower = re.sub(pattern, generic, text_lower, flags=re.IGNORECASE)
    
    return text_lower


def get_generic_name(brand_name: str) -> str | None:
    """
    ================================================================================
    Lookup the generic name for a specific PH brand name (exact match).
    ================================================================================
    Args:
        brand_name (str): Brand name to look up.

    Returns:
        str | None: Generic name if found, else None.
    ================================================================================
    """
    key = r"\b" + re.escape(brand_name.lower()) + r"\b"
    for pattern, generic in PH_BRAND_TO_GENERIC.items():
        if re.search(pattern, brand_name, flags=re.IGNORECASE):
            return generic
    return None


if __name__ == "__main__":
    # Quick sanity check
    test_queries = [
        "Ano ang gamot sa headache? Biogesic o Ponstan?",
        "How much is Ventolin inhaler at Mercury Drug?",
        "May side effects ba ang Neozep?",
    ]
    for q in test_queries:
        print(f"[ORIGINAL]  {q}")
        print(f"[NORMALIZED] {normalize_ph_drug_names(q)}")
        print()

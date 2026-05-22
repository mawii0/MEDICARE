"""
================================================================================
PHARMABOT PH — Philippine Drug Database Generator
================================================================================
Run this script once to generate data/ph_drug_database.jsonl from the inline
master list of ~40 common Philippine medicines (OTC + Rx).

Each record follows the schema required by the BM25 retrieval layer and the
response generator.
================================================================================
"""

import json
import os

# ------------------------------------------------------------------------------
# MASTER DRUG LIST (40 drugs: 20 OTC, 20 Rx)
# ------------------------------------------------------------------------------
MASTER_DRUGS = [
    # =========================================================================
    # OTC DRUGS
    # =========================================================================
    {
        "drug_id": "PH-OTC-001",
        "generic_name": "Paracetamol",
        "drug_class": "Analgesic / Antipyretic",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Biogesic", "manufacturer": "Unilab", "form": "500mg tablet"},
            {"brand": "Tempra", "manufacturer": "J&J Philippines", "form": "500mg tablet / syrup"},
            {"brand": "Panadol", "manufacturer": "GSK", "form": "500mg tablet"},
            {"brand": "Calpol", "manufacturer": "GSK", "form": "Pediatric syrup"},
            {"brand": "Paracetamol Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱1.50 – ₱4.00",
            "biogesic_per_tablet": "₱7.00 – ₱10.00",
            "panadol_per_tablet": "₱8.00 – ₱12.00",
            "source": "Mercury Drug / Rose Pharmacy / Generics Pharmacy (2024 estimate)",
            "note": "Prices may vary by region and pharmacy. Generics Pharmacy and Botika ng Barangay typically offer the lowest prices."
        },
        "indications": ["mild to moderate pain", "fever", "headache", "toothache", "dysmenorrhea"],
        "dosage_adult": "500–1000 mg every 4–6 hours. Maximum: 4000 mg/day.",
        "dosage_pediatric": "10–15 mg/kg every 4–6 hours. Do not exceed 5 doses in 24 hours.",
        "intake_instructions": "Can be taken with or without food. Take with water.",
        "onset_of_action": "30–60 minutes",
        "side_effects_common": ["nausea (rare at normal doses)", "stomach discomfort"],
        "side_effects_serious": ["hepatotoxicity (liver damage) at overdose", "severe skin reactions (rare)"],
        "contraindications": ["severe hepatic impairment", "known hypersensitivity to paracetamol"],
        "drug_interactions": ["warfarin (may increase bleeding risk at high doses)", "alcohol (increases hepatotoxicity risk)"],
        "overdose_note": "Paracetamol overdose is a medical emergency. Seek immediate care. Call 911 or go to the nearest hospital.",
        "storage": "Store below 30°C, away from moisture and sunlight.",
        "pregnancy_category": "Category B — generally considered safe; consult OB-GYN",
        "full_text": "Paracetamol (Biogesic, Tempra, Panadol) is an OTC analgesic and antipyretic used for mild to moderate pain, fever, and headache."
    },
    {
        "drug_id": "PH-OTC-002",
        "generic_name": "Ibuprofen",
        "drug_class": "NSAID / Analgesic / Antipyretic",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Advil", "manufacturer": "GSK", "form": "200mg tablet"},
            {"brand": "Medicol", "manufacturer": "Unilab", "form": "200mg / 400mg capsule"},
            {"brand": "Nurofen", "manufacturer": "Reckitt", "form": "200mg tablet"},
            {"brand": "Ibuprofen Generic", "manufacturer": "Various", "form": "200mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱6.00",
            "advil_per_tablet": "₱8.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["pain", "inflammation", "fever", "dysmenorrhea", "muscle aches"],
        "dosage_adult": "200–400 mg every 4–6 hours as needed. Maximum: 1200 mg/day (OTC).",
        "dosage_pediatric": "5–10 mg/kg every 6–8 hours. Consult pediatrician for children under 6 months.",
        "intake_instructions": "Take with food or milk to reduce stomach upset.",
        "onset_of_action": "30–60 minutes",
        "side_effects_common": ["stomach upset", "heartburn", "nausea", "dizziness"],
        "side_effects_serious": ["GI bleeding", "kidney damage (long-term use)", "allergic reactions"],
        "contraindications": ["peptic ulcer disease", "severe kidney disease", "aspirin-sensitive asthma", "third trimester pregnancy"],
        "drug_interactions": ["aspirin", "warfarin", "other NSAIDs", "methotrexate"],
        "overdose_note": "Seek emergency care for overdose. Symptoms include severe stomach pain, vomiting blood, drowsiness.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — avoid in third trimester; consult OB-GYN",
        "full_text": "Ibuprofen (Advil, Medicol) is an OTC NSAID used for pain, inflammation, fever, and headache. Take with food."
    },
    {
        "drug_id": "PH-OTC-003",
        "generic_name": "Mefenamic Acid",
        "drug_class": "NSAID / Analgesic",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Ponstan", "manufacturer": "Astellas / Pfizer", "form": "500mg tablet"},
            {"brand": "Dolfenal", "manufacturer": "Unilab", "form": "500mg tablet"},
            {"brand": "Feminax", "manufacturer": "Various", "form": "500mg tablet"},
            {"brand": "Mefenamic Acid Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱7.00",
            "ponstan_per_tablet": "₱10.00 – ₱20.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["pain", "dysmenorrhea", "muscle aches", "toothache"],
        "dosage_adult": "500 mg as initial dose, then 250 mg every 6 hours as needed.",
        "dosage_pediatric": "Not recommended for children under 14 years.",
        "intake_instructions": "Take with food to minimize stomach irritation.",
        "onset_of_action": "1 hour",
        "side_effects_common": ["stomach pain", "nausea", "diarrhea", "dizziness"],
        "side_effects_serious": ["GI bleeding", "severe allergic reaction", "liver problems"],
        "contraindications": ["active peptic ulcer", "inflammatory bowel disease", "severe liver or kidney disease", "pregnancy (especially third trimester)"],
        "drug_interactions": ["warfarin", "lithium", "methotrexate", "other NSAIDs"],
        "overdose_note": "Overdose may cause severe GI bleeding and kidney failure. Seek emergency care immediately.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — avoid in third trimester",
        "full_text": "Mefenamic Acid (Ponstan, Dolfenal) is an OTC NSAID for pain, dysmenorrhea, and headache. Take with food."
    },
    {
        "drug_id": "PH-OTC-004",
        "generic_name": "Cetirizine",
        "drug_class": "Antihistamine (second-generation)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zyrtec", "manufacturer": "UCB", "form": "10mg tablet"},
            {"brand": "Allerta", "manufacturer": "Unilab", "form": "10mg tablet / syrup"},
            {"brand": "Ritez", "manufacturer": "Various", "form": "10mg tablet"},
            {"brand": "Cetirizine Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱5.00 – ₱10.00",
            "zyrtec_per_tablet": "₱15.00 – ₱25.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["allergic rhinitis", "urticaria", "hay fever", "itchy eyes", "sneezing"],
        "dosage_adult": "10 mg once daily.",
        "dosage_pediatric": "6–11 years: 5–10 mg once daily. 2–5 years: 2.5 mg once daily.",
        "intake_instructions": "May be taken with or without food. Avoid alcohol.",
        "onset_of_action": "1 hour",
        "side_effects_common": ["drowsiness (less than first-generation antihistamines)", "dry mouth", "fatigue"],
        "side_effects_serious": ["difficulty urinating", "severe allergic reaction (rare)"],
        "contraindications": ["severe renal impairment (dose adjustment needed)", "hypersensitivity to cetirizine"],
        "drug_interactions": ["alcohol (increases sedation)", "other CNS depressants"],
        "overdose_note": "Overdose may cause extreme drowsiness. Seek medical help if suspected.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — generally considered safe; consult OB-GYN",
        "full_text": "Cetirizine (Zyrtec, Allerta) is an OTC second-generation antihistamine for allergies and urticaria."
    },
    {
        "drug_id": "PH-OTC-005",
        "generic_name": "Loratadine",
        "drug_class": "Antihistamine (second-generation)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Claritin", "manufacturer": "Bayer", "form": "10mg tablet"},
            {"brand": "Lortan", "manufacturer": "Unilab", "form": "10mg tablet"},
            {"brand": "Loratadine Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱5.00 – ₱9.00",
            "claritin_per_tablet": "₱14.00 – ₱22.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["allergic rhinitis", "chronic urticaria", "hay fever", "sneezing", "runny nose"],
        "dosage_adult": "10 mg once daily.",
        "dosage_pediatric": "6–12 years: 10 mg once daily. 2–5 years: 5 mg once daily.",
        "intake_instructions": "May be taken with or without food. Non-drowsy for most users.",
        "onset_of_action": "1–3 hours (peak)",
        "side_effects_common": ["headache", "dry mouth", "mild drowsiness (rare)"],
        "side_effects_serious": ["rapid heartbeat", "severe allergic reaction (rare)"],
        "contraindications": ["severe liver disease (dose adjustment needed)", "hypersensitivity to loratadine"],
        "drug_interactions": ["ketoconazole", "erythromycin", "grapefruit juice (may increase levels)"],
        "overdose_note": "Overdose may cause headache, rapid heartbeat, and drowsiness. Seek medical help.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Loratadine (Claritin, Lortan) is an OTC non-drowsy antihistamine for allergies and rhinitis."
    },
    {
        "drug_id": "PH-OTC-006",
        "generic_name": "Loperamide",
        "drug_class": "Antidiarrheal",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Imodium", "manufacturer": "Johnson & Johnson", "form": "2mg capsule"},
            {"brand": "Diatabs", "manufacturer": "Unilab", "form": "2mg capsule"},
            {"brand": "Loperamide Generic", "manufacturer": "Various", "form": "2mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱4.00 – ₱8.00",
            "imodium_per_capsule": "₱12.00 – ₱20.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["acute diarrhea", "travelers' diarrhea"],
        "dosage_adult": "Initial 4 mg, then 2 mg after each loose stool. Maximum: 16 mg/day.",
        "dosage_pediatric": "Consult pediatrician. Not recommended for children under 2 years.",
        "intake_instructions": "Take after each loose bowel movement. Drink oral rehydration salts to prevent dehydration.",
        "onset_of_action": "1 hour",
        "side_effects_common": ["constipation", "dizziness", "nausea", "abdominal cramps"],
        "side_effects_serious": ["toxic megacolon (rare, in infectious diarrhea)", "severe allergic reaction"],
        "contraindications": ["bloody diarrhea", "high fever with diarrhea", "pseudomembranous colitis", "children under 2 years"],
        "drug_interactions": ["antibiotics (if infectious cause suspected, treat cause first)"],
        "overdose_note": "Overdose can cause CNS depression and severe constipation. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Loperamide (Imodium, Diatabs) is an OTC antidiarrheal for acute diarrhea. Use with oral rehydration."
    },
    {
        "drug_id": "PH-OTC-007",
        "generic_name": "Omeprazole",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Prilosec", "manufacturer": "AstraZeneca", "form": "20mg capsule"},
            {"brand": "Omepron", "manufacturer": "Unilab", "form": "20mg capsule"},
            {"brand": "Omeprazole Generic", "manufacturer": "Various", "form": "20mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱6.00 – ₱12.00",
            "prilosec_per_capsule": "₱18.00 – ₱35.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["acid reflux", "heartburn", "GERD (short-term OTC use)", "stomach ulcer prevention"],
        "dosage_adult": "20 mg once daily before breakfast for 14 days. Do not use OTC for more than 14 days without consulting a doctor.",
        "dosage_pediatric": "Not recommended for children under 18 years without medical advice.",
        "intake_instructions": "Take 30–60 minutes before a meal, preferably before breakfast. Swallow whole; do not crush.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["headache", "diarrhea", "nausea", "abdominal pain"],
        "side_effects_serious": ["severe diarrhea (C. difficile infection)", "low magnesium levels (long-term use)", "bone fractures (long-term use)"],
        "contraindications": ["hypersensitivity to omeprazole", "concurrent use with clopidogrel (reduced efficacy)"],
        "drug_interactions": ["clopidogrel", "warfarin", "ketoconazole", "atazanavir"],
        "overdose_note": "Overdose symptoms are usually mild. Seek medical advice if concerned.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Omeprazole (Prilosec, Omepron) is an OTC PPI for heartburn and acid reflux. Take before breakfast."
    },
    {
        "drug_id": "PH-OTC-008",
        "generic_name": "Ascorbic Acid (Vitamin C)",
        "drug_class": "Vitamin Supplement",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Ceelin", "manufacturer": "Unilab", "form": "100mg / 500mg tablet or syrup"},
            {"brand": "Fern-C", "manufacturer": "Fern", "form": "500mg capsule"},
            {"brand": "Conzace", "manufacturer": "Unilab", "form": "multivitamin + zinc capsule"},
            {"brand": "Ascorbic Acid Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱1.00 – ₱3.00",
            "ceelin_per_tablet": "₱5.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["vitamin C deficiency", "immune support", "scurvy prevention"],
        "dosage_adult": "500–1000 mg daily.",
        "dosage_pediatric": "100–300 mg daily depending on age.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "N/A (nutritional supplement)",
        "side_effects_common": ["stomach upset", "diarrhea (at high doses >2000 mg/day)"],
        "side_effects_serious": ["kidney stones (in susceptible individuals at very high doses)"],
        "contraindications": ["history of kidney stones", "hemochromatosis", "G6PD deficiency (high doses)"],
        "drug_interactions": ["warfarin (may reduce effect)", "iron supplements (increases iron absorption)"],
        "overdose_note": "High doses (>2000 mg/day) may cause diarrhea and increase kidney stone risk.",
        "storage": "Store in a cool, dry place.",
        "pregnancy_category": "Category A — safe when taken within recommended doses",
        "full_text": "Ascorbic Acid / Vitamin C (Ceelin, Fern-C) is an OTC vitamin supplement for immune support."
    },
    {
        "drug_id": "PH-OTC-009",
        "generic_name": "Multivitamins",
        "drug_class": "Vitamin / Mineral Supplement",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Berocca", "manufacturer": "Bayer", "form": "effervescent tablet"},
            {"brand": "Supradyn", "manufacturer": "Bayer", "form": "film-coated tablet"},
            {"brand": "Enervon", "manufacturer": "Unilab", "form": "tablet / syrup"},
            {"brand": "Multivitamins Generic", "manufacturer": "Various", "form": "tablet / capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱8.00",
            "berocca_per_tablet": "₱15.00 – ₱25.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["vitamin deficiency", "general wellness", "fatigue", "poor appetite"],
        "dosage_adult": "1 tablet daily or as directed.",
        "dosage_pediatric": "Use pediatric formulations as directed by physician.",
        "intake_instructions": "Take with food to improve absorption of fat-soluble vitamins.",
        "onset_of_action": "N/A (nutritional supplement)",
        "side_effects_common": ["bright yellow urine (from B vitamins)", "mild stomach upset", "nausea"],
        "side_effects_serious": ["allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to any component", "hypervitaminosis A or D"],
        "drug_interactions": ["levodopa", "warfarin", "certain antibiotics"],
        "overdose_note": "Do not exceed recommended dose. Fat-soluble vitamins can accumulate and cause toxicity.",
        "storage": "Store in a cool, dry place.",
        "pregnancy_category": "Category A — use prenatal formulations if pregnant",
        "full_text": "Multivitamins (Berocca, Enervon, Supradyn) are OTC supplements for general wellness and vitamin deficiency."
    },
    {
        "drug_id": "PH-OTC-010",
        "generic_name": "Calcium Carbonate + Vitamin D3",
        "drug_class": "Vitamin / Mineral Supplement",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Caltrate", "manufacturer": "Pfizer", "form": "tablet"},
            {"brand": "Tums", "manufacturer": "GSK", "form": "chewable tablet"},
            {"brand": "Calcium + Vitamin D Generic", "manufacturer": "Various", "form": "tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱4.00 – ₱10.00",
            "caltrate_per_tablet": "₱12.00 – ₱25.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["calcium deficiency", "osteoporosis prevention", "bone health"],
        "dosage_adult": "1 tablet 1–2 times daily with meals.",
        "dosage_pediatric": "As directed by pediatrician.",
        "intake_instructions": "Take with meals for best absorption. Do not take with iron supplements at the same time.",
        "onset_of_action": "N/A (nutritional supplement)",
        "side_effects_common": ["constipation", "gas", "bloating"],
        "side_effects_serious": ["hypercalcemia (with excessive doses)", "kidney stones"],
        "contraindications": ["hypercalcemia", "severe kidney disease", "kidney stones"],
        "drug_interactions": ["iron supplements", "levothyroxine", "certain antibiotics (tetracyclines, fluoroquinolones)"],
        "overdose_note": "Excessive calcium may cause constipation, confusion, and kidney stones. Seek medical advice.",
        "storage": "Store in a cool, dry place.",
        "pregnancy_category": "Category A — safe within recommended doses",
        "full_text": "Calcium Carbonate + Vitamin D3 (Caltrate, Tums) is an OTC supplement for bone health and calcium deficiency."
    },
    {
        "drug_id": "PH-OTC-011",
        "generic_name": "Hydrocortisone (topical)",
        "drug_class": "Corticosteroid (topical)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Hydrocortisone Cream Generic", "manufacturer": "Various", "form": "1% cream"},
            {"brand": "Cortaid", "manufacturer": "Various", "form": "1% cream"}
        ],
        "ph_price_estimates": {
            "generic_per_tube": "₱50.00 – ₱120.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["mild skin rashes", "insect bites", "eczema (mild)", "dermatitis"],
        "dosage_adult": "Apply thin layer to affected area 1–2 times daily for up to 7 days.",
        "dosage_pediatric": "Consult pediatrician before use on children.",
        "intake_instructions": "For external use only. Do not apply on face, broken skin, or large areas.",
        "onset_of_action": "Several hours to days",
        "side_effects_common": ["skin thinning (with prolonged use)", "burning sensation", "dryness"],
        "side_effects_serious": ["skin infection worsening", "allergic reaction to cream base"],
        "contraindications": ["bacterial, viral, or fungal skin infections", "acne", "rosacea"],
        "drug_interactions": ["other topical medications (may increase absorption)"],
        "overdose_note": "Excessive or prolonged use can cause skin thinning and systemic absorption effects.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN before use",
        "full_text": "Hydrocortisone 1% cream is an OTC topical corticosteroid for mild skin rashes and insect bites."
    },
    {
        "drug_id": "PH-OTC-012",
        "generic_name": "Clotrimazole (topical/oral)",
        "drug_class": "Antifungal",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Canesten", "manufacturer": "Bayer", "form": "1% cream / pessary"},
            {"brand": "Clotrimazole Generic", "manufacturer": "Various", "form": "1% cream / oral troche"}
        ],
        "ph_price_estimates": {
            "generic_per_tube": "₱40.00 – ₱100.00",
            "canesten_per_tube": "₱120.00 – ₱200.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["athlete's foot", "jock itch", "ringworm", "vaginal yeast infection", "oral thrush (troche)"],
        "dosage_adult": "Topical: apply 2–3 times daily for 2–4 weeks. Vaginal: insert pessary at bedtime for 3–7 nights.",
        "dosage_pediatric": "Consult pediatrician.",
        "intake_instructions": "Clean and dry affected area before applying. Continue treatment for 1–2 weeks after symptoms clear.",
        "onset_of_action": "Few days for symptom relief; full clearance in 2–4 weeks",
        "side_effects_common": ["local irritation", "burning", "redness"],
        "side_effects_serious": ["severe allergic reaction (rare)"],
        "contraindications": ["hypersensitivity to clotrimazole"],
        "drug_interactions": ["latex condoms and diaphragms (vaginal cream may weaken latex)"],
        "overdose_note": "Topical overdose is unlikely. Ingestion of large amounts may cause GI upset.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN for vaginal use during pregnancy",
        "full_text": "Clotrimazole (Canesten) is an OTC antifungal for skin and vaginal yeast infections."
    },
    {
        "drug_id": "PH-OTC-013",
        "generic_name": "Phenylephrine / Paracetamol / Chlorphenamine",
        "drug_class": "Decongestant / Analgesic / Antihistamine (combination)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Neozep", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Decolgen", "manufacturer": "Unilab", "form": "tablet / syrup"},
            {"brand": "Bioflu", "manufacturer": "Unilab", "form": "tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱4.00 – ₱8.00",
            "neozep_per_tablet": "₱6.00 – ₱12.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["common cold", "flu symptoms", "nasal congestion", "fever", "runny nose", "sneezing"],
        "dosage_adult": "1 tablet every 6 hours as needed. Maximum: 4 tablets/day.",
        "dosage_pediatric": "Use pediatric formulations. Consult pediatrician for children under 6 years.",
        "intake_instructions": "May cause drowsiness. Avoid alcohol and driving. Take with food if stomach upset occurs.",
        "onset_of_action": "30–60 minutes",
        "side_effects_common": ["drowsiness", "dry mouth", "nausea", "dizziness"],
        "side_effects_serious": ["severe allergic reaction", "difficulty urinating", "rapid heartbeat"],
        "contraindications": ["severe hypertension", "MAOI use within 14 days", "glaucoma", "urinary retention"],
        "drug_interactions": ["MAOIs", "other sedatives", "alcohol", "antihypertensives"],
        "overdose_note": "Overdose can cause severe drowsiness, rapid heartbeat, and liver damage (from paracetamol). Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Neozep / Decolgen / Bioflu are OTC combination cold medicines for fever, congestion, and runny nose. May cause drowsiness."
    },
    {
        "drug_id": "PH-OTC-014",
        "generic_name": "Dextromethorphan / Guaifenesin",
        "drug_class": "Antitussive / Expectorant (combination)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Tuseran", "manufacturer": "Unilab", "form": "capsule / syrup"},
            {"brand": "Robitussin DM", "manufacturer": "Pfizer", "form": "syrup"},
            {"brand": "Ambrolex DM", "manufacturer": "Various", "form": "syrup"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱5.00 – ₱10.00",
            "tuseran_per_capsule": "₱8.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["dry cough", "productive cough", "chest congestion"],
        "dosage_adult": "1 capsule or 10–20 mL syrup every 6–8 hours. Maximum: 4 doses/day.",
        "dosage_pediatric": "Use pediatric formulations. Consult pediatrician for children under 2 years.",
        "intake_instructions": "Take with water. Drink plenty of fluids.",
        "onset_of_action": "15–30 minutes",
        "side_effects_common": ["drowsiness", "dizziness", "nausea", "stomach upset"],
        "side_effects_serious": ["severe allergic reaction", "confusion (at high doses)", "serotonin syndrome (if combined with MAOIs/SSRIs)"],
        "contraindications": ["MAOI use within 14 days", "chronic cough from smoking or asthma (without medical advice)"],
        "drug_interactions": ["MAOIs", "SSRIs/SNRIs", "other sedatives"],
        "overdose_note": "High doses of dextromethorphan can cause hallucinations and CNS depression. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Tuseran / Robitussin DM are OTC cough medicines combining a cough suppressant and expectorant."
    },
    {
        "drug_id": "PH-OTC-015",
        "generic_name": "Carbocisteine",
        "drug_class": "Mucolytic",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Solmux", "manufacturer": "Unilab", "form": "500mg capsule / syrup"},
            {"brand": "Carbocisteine Generic", "manufacturer": "Various", "form": "500mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱4.00 – ₱8.00",
            "solmux_per_capsule": "₱8.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["productive cough", "thick phlegm", "bronchitis", "COPD adjunct"],
        "dosage_adult": "500 mg 3–4 times daily.",
        "dosage_pediatric": "Children: 250 mg 3–4 times daily. Consult pediatrician for children under 2 years.",
        "intake_instructions": "Take with meals to reduce stomach upset. Drink plenty of water.",
        "onset_of_action": "Several days for full effect",
        "side_effects_common": ["stomach upset", "nausea", "diarrhea", "skin rash"],
        "side_effects_serious": ["severe allergic reaction", "GI bleeding (rare)"],
        "contraindications": ["active peptic ulcer", "hypersensitivity to carbocisteine"],
        "drug_interactions": ["cough suppressants (may trap mucus if used together)"],
        "overdose_note": "Overdose may cause severe GI upset. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Carbocisteine (Solmux) is an OTC mucolytic for productive cough and thick phlegm. Take with meals."
    },
    {
        "drug_id": "PH-OTC-016",
        "generic_name": "Aluminum Hydroxide / Magnesium Hydroxide",
        "drug_class": "Antacid",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Maalox", "manufacturer": "Sanofi", "form": "suspension / tablet"},
            {"brand": "Kremil-S", "manufacturer": "Unilab", "form": "tablet"},
            {"brand": "Antacid Generic", "manufacturer": "Various", "form": "suspension / tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱6.00",
            "maalox_per_bottle": "₱80.00 – ₱150.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["heartburn", "acid indigestion", "sour stomach", "hyperacidity"],
        "dosage_adult": "1–2 tablets or 5–10 mL suspension after meals and at bedtime.",
        "dosage_pediatric": "Consult pediatrician.",
        "intake_instructions": "Chew tablets thoroughly before swallowing. Shake suspension well before use.",
        "onset_of_action": "Immediate relief (minutes)",
        "side_effects_common": ["constipation (aluminum)", "diarrhea (magnesium)", "chalky taste"],
        "side_effects_serious": ["kidney problems (with long-term use in kidney disease)", "hypermagnesemia"],
        "contraindications": ["severe kidney disease", "hypophosphatemia"],
        "drug_interactions": ["tetracyclines", "fluoroquinolones", "iron supplements", "levothyroxine (separate by 2–4 hours)"],
        "overdose_note": "Excessive use can cause constipation or diarrhea and electrolyte imbalances. Seek medical advice.",
        "storage": "Store below 30°C. Do not freeze suspension.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Aluminum/Magnesium Hydroxide (Maalox, Kremil-S) is an OTC antacid for heartburn and hyperacidity."
    },
    {
        "drug_id": "PH-OTC-017",
        "generic_name": "Oral Rehydration Salts (ORS)",
        "drug_class": "Electrolyte Replacement",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Hydrite", "manufacturer": "Unilab", "form": "powder sachet"},
            {"brand": "Pedialyte", "manufacturer": "Abbott", "form": "powder / ready-to-drink"},
            {"brand": "Oral Rehydration Salts Generic", "manufacturer": "Various", "form": "powder sachet"}
        ],
        "ph_price_estimates": {
            "generic_per_sachet": "₱5.00 – ₱15.00",
            "hydrite_per_sachet": "₱10.00 – ₱20.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["dehydration", "diarrhea", "vomiting", "heat exhaustion"],
        "dosage_adult": "Dissolve 1 sachet in 1 liter of clean water. Drink as much as wanted.",
        "dosage_pediatric": "Give small frequent sips. Consult pediatrician for severe dehydration.",
        "intake_instructions": "Dissolve completely in clean water. Do not add sugar or other substances.",
        "onset_of_action": "Minutes to hours depending on dehydration severity",
        "side_effects_common": ["mild nausea if taken too quickly", "abdominal bloating"],
        "side_effects_serious": ["electrolyte imbalance (if wrong concentration prepared)"],
        "contraindications": ["severe dehydration (requires IV fluids)", "inability to drink", "bowel obstruction"],
        "drug_interactions": ["none significant"],
        "overdose_note": "Overconsumption may cause electrolyte imbalance. Prepare exactly as directed.",
        "storage": "Store in a cool, dry place.",
        "pregnancy_category": "Category A — safe",
        "full_text": "Oral Rehydration Salts (Hydrite, Pedialyte) are OTC electrolyte replacements for dehydration from diarrhea."
    },
    {
        "drug_id": "PH-OTC-018",
        "generic_name": "Diphenhydramine",
        "drug_class": "Antihistamine (first-generation)",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Benadryl", "manufacturer": "J&J", "form": "25mg capsule / syrup"},
            {"brand": "Diphenhydramine Generic", "manufacturer": "Various", "form": "25mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱4.00 – ₱8.00",
            "benadryl_per_capsule": "₱10.00 – ₱18.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["allergies", "urticaria", "motion sickness", "insomnia (short-term)", "cough (in combination products)"],
        "dosage_adult": "25–50 mg every 4–6 hours. Maximum: 300 mg/day.",
        "dosage_pediatric": "Consult pediatrician. Not recommended for children under 2 years.",
        "intake_instructions": "May cause significant drowsiness. Avoid alcohol and operating machinery.",
        "onset_of_action": "15–30 minutes",
        "side_effects_common": ["severe drowsiness", "dry mouth", "blurred vision", "constipation"],
        "side_effects_serious": ["urinary retention", "confusion (especially in elderly)", "severe allergic reaction"],
        "contraindications": ["glaucoma", "enlarged prostate / urinary retention", "asthma (may thicken secretions)", "pregnancy (especially first trimester)"],
        "drug_interactions": ["alcohol", "other sedatives", "MAOIs"],
        "overdose_note": "Overdose causes severe anticholinergic symptoms: delirium, hallucinations, seizures. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Diphenhydramine (Benadryl) is an OTC first-generation antihistamine for allergies and motion sickness. Causes drowsiness."
    },
    {
        "drug_id": "PH-OTC-019",
        "generic_name": "Ambroxol",
        "drug_class": "Mucolytic / Expectorant",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Ambrolex", "manufacturer": "Unilab", "form": "30mg tablet / syrup"},
            {"brand": "Mucosolvan", "manufacturer": "Boehringer", "form": "30mg tablet / syrup"},
            {"brand": "Ambroxol Generic", "manufacturer": "Various", "form": "30mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱4.00 – ₱8.00",
            "ambrolex_per_tablet": "₱8.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["productive cough", "thick mucus", "bronchitis"],
        "dosage_adult": "30 mg 3 times daily after meals.",
        "dosage_pediatric": "Use pediatric formulations as directed.",
        "intake_instructions": "Take after meals with water.",
        "onset_of_action": "30 minutes",
        "side_effects_common": ["nausea", "stomach upset", "vomiting", "skin rash"],
        "side_effects_serious": ["severe allergic reaction", "anaphylaxis (rare)"],
        "contraindications": ["hypersensitivity to ambroxol", "first trimester pregnancy"],
        "drug_interactions": ["cough suppressants (may reduce expectoration)"],
        "overdose_note": "Overdose may cause severe GI symptoms. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — avoid in first trimester; consult OB-GYN",
        "full_text": "Ambroxol (Ambrolex, Mucosolvan) is an OTC mucolytic for productive cough and thick mucus."
    },
    {
        "drug_id": "PH-OTC-020",
        "generic_name": "Povidone-Iodine",
        "drug_class": "Topical Antiseptic",
        "rx_status": "OTC",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Betadine", "manufacturer": "Mundipharma", "form": "solution / ointment / gargle"},
            {"brand": "Povidone-Iodine Generic", "manufacturer": "Various", "form": "solution"}
        ],
        "ph_price_estimates": {
            "generic_per_bottle": "₱40.00 – ₱100.00",
            "betadine_per_bottle": "₱100.00 – ₱250.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["minor cuts", "wounds", "abrasions", "skin disinfection", "sore throat gargle"],
        "dosage_adult": "Apply to affected area 1–3 times daily. For gargle: dilute and gargle 2–3 times daily.",
        "dosage_pediatric": "Consult pediatrician before use on infants.",
        "intake_instructions": "For external use only. Do not swallow.",
        "onset_of_action": "Immediate",
        "side_effects_common": ["skin staining (brown)", "local irritation", "burning sensation"],
        "side_effects_serious": ["thyroid dysfunction (with prolonged use on large areas)", "severe allergic reaction (rare)"],
        "contraindications": ["iodine allergy", "thyroid disorders (prolonged use on large areas)", "newborns (use with caution)"],
        "drug_interactions": ["lithium", "radioactive iodine diagnostics"],
        "overdose_note": "Ingestion can cause iodine toxicity. Seek emergency care if swallowed in large amounts.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — avoid prolonged use on large areas; consult OB-GYN",
        "full_text": "Povidone-Iodine (Betadine) is an OTC topical antiseptic for cuts, wounds, and minor infections."
    },

    # =========================================================================
    # RX DRUGS
    # =========================================================================
    {
        "drug_id": "PH-RX-001",
        "generic_name": "Amoxicillin",
        "drug_class": "Penicillin-type Antibiotic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Amoxil", "manufacturer": "GSK", "form": "500mg capsule"},
            {"brand": "Himox", "manufacturer": "Unilab", "form": "500mg capsule / suspension"},
            {"brand": "Amolin", "manufacturer": "Various", "form": "500mg capsule"},
            {"brand": "Amoxicillin Generic", "manufacturer": "Various", "form": "500mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱5.00 – ₱12.00",
            "amoxil_per_capsule": "₱15.00 – ₱30.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["respiratory tract infections", "urinary tract infections", "skin infections", "otitis media"],
        "dosage_adult": "As prescribed by physician. Typical: 500 mg every 8 hours for 7–10 days depending on infection.",
        "dosage_pediatric": "As prescribed by pediatrician. Typical: 20–40 mg/kg/day divided every 8 hours.",
        "intake_instructions": "Take with or without food. Complete full course even if symptoms improve.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["nausea", "diarrhea", "skin rash", "vomiting"],
        "side_effects_serious": ["severe allergic reaction (anaphylaxis)", "Stevens-Johnson syndrome", "C. difficile colitis"],
        "contraindications": ["penicillin allergy", "infectious mononucleosis (high rash risk)"],
        "drug_interactions": ["warfarin", "allopurinol", "methotrexate", "probenecid"],
        "overdose_note": "Overdose may cause crystaluria and neurotoxicity. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — generally considered safe; consult OB-GYN",
        "full_text": "Amoxicillin (Amoxil, Himox) is a prescription penicillin antibiotic for bacterial infections. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-002",
        "generic_name": "Azithromycin",
        "drug_class": "Macrolide Antibiotic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Zithromax", "manufacturer": "Pfizer", "form": "500mg tablet / suspension"},
            {"brand": "Azee", "manufacturer": "Cipla", "form": "500mg tablet"},
            {"brand": "Azithromycin Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱20.00 – ₱40.00",
            "zithromax_per_tablet": "₱60.00 – ₱120.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["respiratory infections", "skin infections", "sexually transmitted infections (e.g., chlamydia)", "typhoid fever"],
        "dosage_adult": "As prescribed by physician. Typical: 500 mg once daily for 3 days, or 500 mg on day 1 then 250 mg days 2–5.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take 1 hour before or 2 hours after meals. Antacids may reduce absorption.",
        "onset_of_action": "2–3 hours",
        "side_effects_common": ["nausea", "diarrhea", "abdominal pain", "vomiting"],
        "side_effects_serious": ["liver damage", "severe allergic reaction", "QT prolongation / arrhythmia"],
        "contraindications": ["hypersensitivity to azithromycin or other macrolides", "severe liver disease", "history of QT prolongation"],
        "drug_interactions": ["warfarin", "digoxin", "statins", "antiarrhythmics"],
        "overdose_note": "Overdose may cause severe hearing loss, liver damage, and cardiac arrhythmias. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Azithromycin (Zithromax, Azee) is a prescription macrolide antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-003",
        "generic_name": "Cefalexin",
        "drug_class": "Cephalosporin Antibiotic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Keflex", "manufacturer": "Advancis", "form": "500mg capsule"},
            {"brand": "Sporidex", "manufacturer": "Cipla", "form": "500mg capsule"},
            {"brand": "Cefalexin Generic", "manufacturer": "Various", "form": "500mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱8.00 – ₱15.00",
            "keflex_per_capsule": "₱25.00 – ₱50.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["respiratory tract infections", "skin infections", "UTIs", "otitis media"],
        "dosage_adult": "As prescribed by physician. Typical: 250–500 mg every 6 hours.",
        "dosage_pediatric": "As prescribed by pediatrician. Typical: 25–50 mg/kg/day divided every 6 hours.",
        "intake_instructions": "Take with food if stomach upset occurs.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["diarrhea", "nausea", "vomiting", "skin rash"],
        "side_effects_serious": ["severe allergic reaction (anaphylaxis)", "C. difficile colitis", " Stevens-Johnson syndrome"],
        "contraindications": ["cephalosporin allergy", "penicillin allergy (cross-reactivity risk)"],
        "drug_interactions": ["probenecid", "metformin", "warfarin"],
        "overdose_note": "Overdose may cause nausea, vomiting, and diarrhea. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Cefalexin (Keflex, Sporidex) is a prescription cephalosporin antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-004",
        "generic_name": "Amoxicillin-Clavulanate",
        "drug_class": "Penicillin + Beta-Lactamase Inhibitor",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Augmentin", "manufacturer": "GSK", "form": "625mg tablet / suspension"},
            {"brand": "Amoclav", "manufacturer": "Unilab", "form": "625mg tablet / suspension"},
            {"brand": "Amoxicillin-Clavulanate Generic", "manufacturer": "Various", "form": "625mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱15.00 – ₱30.00",
            "augmentin_per_tablet": "₱40.00 – ₱80.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["respiratory infections", "sinusitis", "UTIs", "skin infections resistant to amoxicillin alone"],
        "dosage_adult": "As prescribed by physician. Typical: 625 mg every 8–12 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach upset. Complete full course.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["diarrhea", "nausea", "vomiting", "skin rash"],
        "side_effects_serious": ["severe allergic reaction", "hepatotoxicity", "C. difficile colitis"],
        "contraindications": ["penicillin allergy", "history of cholestatic jaundice with amoxicillin-clavulanate"],
        "drug_interactions": ["warfarin", "allopurinol", "methotrexate", "probenecid"],
        "overdose_note": "Overdose may cause severe GI symptoms and liver dysfunction. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Amoxicillin-Clavulanate (Augmentin, Amoclav) is a prescription antibiotic combination. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-005",
        "generic_name": "Metformin",
        "drug_class": "Biguanide Antidiabetic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Glucophage", "manufacturer": "Merck", "form": "500mg / 850mg tablet"},
            {"brand": "Glycomet", "manufacturer": "USV", "form": "500mg tablet"},
            {"brand": "Metformin Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱8.00",
            "glucophage_per_tablet": "₱15.00 – ₱30.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["Type 2 Diabetes Mellitus", "polycystic ovary syndrome (PCOS)"],
        "dosage_adult": "As prescribed by physician. Typical starting: 500 mg twice daily with meals.",
        "dosage_pediatric": "Not typically used in children unless directed by specialist.",
        "intake_instructions": "Take with meals to reduce GI side effects. Swallow extended-release tablets whole.",
        "onset_of_action": "2–3 hours (glucose lowering effect)",
        "side_effects_common": ["nausea", "diarrhea", "stomach upset", "metallic taste"],
        "side_effects_serious": ["lactic acidosis (rare but life-threatening)", "vitamin B12 deficiency (long-term use)"],
        "contraindications": ["severe kidney disease", "metabolic acidosis", "severe infection", "contrast dye use (temporary hold)"],
        "drug_interactions": ["contrast media", "alcohol (increases lactic acidosis risk)", "cimetidine", "corticosteroids"],
        "overdose_note": "Overdose can cause lactic acidosis. Seek emergency care immediately.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN; insulin preferred in pregnancy",
        "full_text": "Metformin (Glucophage, Glycomet) is a prescription antidiabetic for Type 2 Diabetes. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-006",
        "generic_name": "Amlodipine",
        "drug_class": "Calcium Channel Blocker (Antihypertensive)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Norvasc", "manufacturer": "Pfizer", "form": "5mg / 10mg tablet"},
            {"brand": "Amlopin", "manufacturer": "Unilab", "form": "5mg tablet"},
            {"brand": "Amlodipine Generic", "manufacturer": "Various", "form": "5mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱3.00 – ₱7.00",
            "norvasc_per_tablet": "₱18.00 – ₱30.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["hypertension", "angina", "chronic stable angina"],
        "dosage_adult": "As prescribed by physician. Typical: 5 mg once daily; may increase to 10 mg.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take at the same time each day. May be taken with or without food.",
        "onset_of_action": "6–12 hours (blood pressure reduction); 1–2 weeks for full effect",
        "side_effects_common": ["ankle swelling", "flushing", "headache", "dizziness", "fatigue"],
        "side_effects_serious": ["severe hypotension", "worsening angina (rare)", "allergic reaction"],
        "contraindications": ["severe aortic stenosis", "hypersensitivity to amlodipine", "cardiogenic shock"],
        "drug_interactions": ["simvastatin (dose limitation)", "other antihypertensives", "grapefruit juice"],
        "overdose_note": "Overdose causes severe hypotension and reflex tachycardia. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Amlodipine (Norvasc, Amlopin) is a prescription calcium channel blocker for hypertension. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-007",
        "generic_name": "Losartan",
        "drug_class": "Angiotensin II Receptor Blocker (ARB)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Cozaar", "manufacturer": "Merck", "form": "50mg / 100mg tablet"},
            {"brand": "Losartan Generic", "manufacturer": "Various", "form": "50mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱5.00 – ₱12.00",
            "cozaar_per_tablet": "₱20.00 – ₱40.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["hypertension", "diabetic nephropathy", "heart failure"],
        "dosage_adult": "As prescribed by physician. Typical: 50 mg once daily; may increase to 100 mg.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "May be taken with or without food.",
        "onset_of_action": "1 hour (peak); 3–6 weeks for full blood pressure control",
        "side_effects_common": ["dizziness", "fatigue", "upper respiratory infection", "back pain"],
        "side_effects_serious": ["hyperkalemia", "acute kidney injury", "severe hypotension", "angioedema (rare)"],
        "contraindications": ["pregnancy (second and third trimesters)", "bilateral renal artery stenosis", "hypersensitivity to losartan"],
        "drug_interactions": ["potassium supplements", "NSAIDs (reduce renal protection)", "lithium", "other antihypertensives"],
        "overdose_note": "Overdose causes hypotension and tachycardia. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category D — contraindicated in 2nd and 3rd trimesters",
        "full_text": "Losartan (Cozaar) is a prescription ARB for hypertension and kidney protection in diabetes. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-008",
        "generic_name": "Atorvastatin",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Lipitor", "manufacturer": "Pfizer", "form": "10mg / 20mg / 40mg tablet"},
            {"brand": "Atorva", "manufacturer": "Zydus", "form": "10mg tablet"},
            {"brand": "Atorvastatin Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱10.00 – ₱20.00",
            "lipitor_per_tablet": "₱40.00 – ₱90.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["high cholesterol", "dyslipidemia", "cardiovascular disease prevention"],
        "dosage_adult": "As prescribed by physician. Typical: 10–20 mg once daily at bedtime.",
        "dosage_pediatric": "As prescribed by pediatrician for familial hypercholesterolemia.",
        "intake_instructions": "Take at any time of day, but bedtime is common. May be taken with or without food. Avoid grapefruit juice.",
        "onset_of_action": "2 weeks (cholesterol reduction); 4 weeks for full effect",
        "side_effects_common": ["muscle aches", "headache", "nausea", "constipation"],
        "side_effects_serious": ["rhabdomyolysis (severe muscle breakdown)", "liver damage", "diabetes risk (long-term)"],
        "contraindications": ["active liver disease", "pregnancy", "breastfeeding", "unexplained elevated liver enzymes"],
        "drug_interactions": ["erythromycin", "clarithromycin", "grapefruit juice", "other statins", "fibrates"],
        "overdose_note": "Overdose may worsen muscle and liver side effects. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category X — contraindicated in pregnancy",
        "full_text": "Atorvastatin (Lipitor, Atorva) is a prescription statin for high cholesterol. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-009",
        "generic_name": "Salbutamol",
        "drug_class": "Short-Acting Beta-2 Agonist (SABA)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Ventolin", "manufacturer": "GSK", "form": "100mcg inhaler / 2mg / 4mg tablet"},
            {"brand": "Asthalin", "manufacturer": "Cipla", "form": "100mcg inhaler"},
            {"brand": "Salbutamol Generic", "manufacturer": "Various", "form": "2mg tablet / nebule"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱8.00 – ₱15.00",
            "ventolin_inhaler": "₱180.00 – ₱350.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["asthma", "bronchospasm", "COPD", "exercise-induced bronchospasm"],
        "dosage_adult": "As prescribed by physician. Inhaler: 1–2 puffs every 4–6 hours as needed.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Shake inhaler before use. Rinse mouth after inhaler use to prevent thrush.",
        "onset_of_action": "5–15 minutes (inhaler)",
        "side_effects_common": ["tremor", "nervousness", "palpitations", "headache"],
        "side_effects_serious": ["paradoxical bronchospasm", "severe hypokalemia", "chest pain"],
        "contraindications": ["hypersensitivity to salbutamol", "tachyarrhythmias"],
        "drug_interactions": ["beta-blockers (non-selective may antagonize effect)", "diuretics (increase hypokalemia risk)", "digoxin"],
        "overdose_note": "Overdose causes severe tachycardia, tremors, and hypokalemia. Seek emergency care.",
        "storage": "Store below 30°C. Keep inhaler away from heat and direct sunlight.",
        "pregnancy_category": "Category C — consult OB-GYN; benefits may outweigh risks in uncontrolled asthma",
        "full_text": "Salbutamol (Ventolin, Asthalin) is a prescription bronchodilator for asthma. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-010",
        "generic_name": "Montelukast",
        "drug_class": "Leukotriene Receptor Antagonist",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Singulair", "manufacturer": "Merck", "form": "10mg tablet / 4mg chewable"},
            {"brand": "Montelukast Generic", "manufacturer": "Various", "form": "10mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱15.00 – ₱30.00",
            "singulair_per_tablet": "₱50.00 – ₱100.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["asthma maintenance", "allergic rhinitis", "exercise-induced bronchospasm prevention"],
        "dosage_adult": "As prescribed by physician. Typical: 10 mg once daily in the evening.",
        "dosage_pediatric": "As prescribed by pediatrician. 6–14 years: 5 mg chewable. 2–5 years: 4 mg chewable.",
        "intake_instructions": "Take in the evening. May be taken with or without food.",
        "onset_of_action": "1 day (clinical effect); may take 1–2 weeks for full benefit",
        "side_effects_common": ["headache", "abdominal pain", "cough", "fever"],
        "side_effects_serious": ["neuropsychiatric effects (agitation, depression, suicidal thoughts)", "severe allergic reaction"],
        "contraindications": ["hypersensitivity to montelukast"],
        "drug_interactions": ["phenobarbital", "rifampin (may reduce levels)", "CYP inducers"],
        "overdose_note": "Overdose may cause abdominal pain, thirst, and headache. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Montelukast (Singulair) is a prescription leukotriene antagonist for asthma and allergies. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-011",
        "generic_name": "Prednisone",
        "drug_class": "Corticosteroid (Systemic)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Prednisone Generic", "manufacturer": "Various", "form": "5mg / 10mg / 20mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱5.00 – ₱15.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["inflammatory conditions", "allergic reactions", "asthma exacerbations", "autoimmune disorders", "certain cancers"],
        "dosage_adult": "As prescribed by physician. Dose varies widely by condition.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach irritation. Do not stop abruptly if used long-term.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["increased appetite", "weight gain", "mood changes", "insomnia", "stomach upset"],
        "side_effects_serious": ["adrenal suppression (long-term use)", "osteoporosis", "diabetes", "severe infections", "Cushing's syndrome"],
        "contraindications": ["systemic fungal infections", "live vaccines (while on high doses)", "hypersensitivity"],
        "drug_interactions": ["NSAIDs (increased GI bleeding risk)", "warfarin", "diuretics", "vaccines"],
        "overdose_note": "Overdose may cause severe fluid retention, high blood pressure, and electrolyte imbalance. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN",
        "full_text": "Prednisone is a prescription systemic corticosteroid for inflammation and autoimmune conditions. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-012",
        "generic_name": "Ciprofloxacin",
        "drug_class": "Fluoroquinolone Antibiotic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Cipro", "manufacturer": "Bayer", "form": "500mg tablet"},
            {"brand": "Cifran", "manufacturer": "Ranbaxy", "form": "500mg tablet"},
            {"brand": "Ciprofloxacin Generic", "manufacturer": "Various", "form": "500mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱15.00 – ₱30.00",
            "cipro_per_tablet": "₱40.00 – ₱80.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["UTIs", "respiratory infections", "skin infections", "typhoid fever", "gastrointestinal infections"],
        "dosage_adult": "As prescribed by physician. Typical: 250–750 mg every 12 hours.",
        "dosage_pediatric": "Generally avoided in children unless no alternatives; as prescribed by pediatrician.",
        "intake_instructions": "Take with water. Avoid taking with dairy products, antacids, or iron supplements (separate by 2 hours). Avoid excessive sunlight.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["nausea", "diarrhea", "stomach upset", "dizziness"],
        "side_effects_serious": ["tendon rupture", "peripheral neuropathy", "QT prolongation", "aortic aneurysm risk", "C. difficile colitis"],
        "contraindications": ["history of tendon disorders with quinolones", "pregnancy", "breastfeeding", "children/adolescents (growth cartilage risk)"],
        "drug_interactions": ["antacids", "iron", "dairy", "warfarin", "theophylline", "caffeine"],
        "overdose_note": "Overdose may cause seizures and renal failure. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — generally avoided in pregnancy",
        "full_text": "Ciprofloxacin (Cipro, Cifran) is a prescription fluoroquinolone antibiotic. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-013",
        "generic_name": "Metronidazole",
        "drug_class": "Nitroimidazole Antibiotic / Antiprotozoal",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Flagyl", "manufacturer": "Sanofi", "form": "500mg tablet"},
            {"brand": "Metronidazole Generic", "manufacturer": "Various", "form": "500mg tablet / suspension"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱8.00 – ₱18.00",
            "flagyl_per_tablet": "₱20.00 – ₱40.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["bacterial vaginosis", "amebiasis", "giardiasis", "dental infections", "C. difficile infection", "H. pylori eradication"],
        "dosage_adult": "As prescribed by physician. Typical: 250–500 mg every 8 hours.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take with food to reduce stomach upset. AVOID ALCOHOL during treatment and for 48 hours after last dose.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["nausea", "metallic taste", "stomach upset", "dark urine (harmless)"],
        "side_effects_serious": ["peripheral neuropathy (long-term use)", "seizures", "severe allergic reaction"],
        "contraindications": ["first trimester pregnancy", "alcohol use during and shortly after therapy", "hypersensitivity"],
        "drug_interactions": ["alcohol (disulfiram-like reaction)", "warfarin", "lithium"],
        "overdose_note": "Overdose may cause seizures and peripheral neuropathy. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — avoid in first trimester; consult OB-GYN",
        "full_text": "Metronidazole (Flagyl) is a prescription antibiotic and antiprotozoal. Requires a doctor's prescription. Avoid alcohol."
    },
    {
        "drug_id": "PH-RX-014",
        "generic_name": "Doxycycline",
        "drug_class": "Tetracycline Antibiotic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Vibramycin", "manufacturer": "Pfizer", "form": "100mg capsule"},
            {"brand": "Doxycycline Generic", "manufacturer": "Various", "form": "100mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱10.00 – ₱20.00",
            "vibramycin_per_capsule": "₱30.00 – ₱60.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["respiratory infections", "skin infections", "UTIs", "tick-borne diseases", "acne", "malaria prophylaxis"],
        "dosage_adult": "As prescribed by physician. Typical: 100 mg every 12 hours on day 1, then 100 mg daily.",
        "dosage_pediatric": "As prescribed by pediatrician. Avoid in children under 8 years (tooth discoloration).",
        "intake_instructions": "Take with food if stomach upset occurs. Drink plenty of water. Avoid lying down for 30 minutes after taking. Avoid sun exposure.",
        "onset_of_action": "1–2 hours",
        "side_effects_common": ["nausea", "stomach upset", "photosensitivity", "vaginal yeast infection"],
        "side_effects_serious": ["esophageal ulceration", "intracranial hypertension", "severe allergic reaction"],
        "contraindications": ["pregnancy", "children under 8 years", "hypersensitivity to tetracyclines"],
        "drug_interactions": ["antacids", "iron", "calcium", "warfarin", "oral contraceptives (may reduce efficacy)", "isotretinoin"],
        "overdose_note": "Overdose may cause severe GI irritation and liver damage. Seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category D — contraindicated in pregnancy",
        "full_text": "Doxycycline (Vibramycin) is a prescription tetracycline antibiotic. Requires a doctor's prescription. Avoid in pregnancy and children under 8."
    },
    {
        "drug_id": "PH-RX-015",
        "generic_name": "Clonazepam",
        "drug_class": "Benzodiazepine (Controlled Substance)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Rivotril", "manufacturer": "Roche", "form": "0.5mg / 2mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱15.00 – ₱30.00",
            "rivotril_per_tablet": "₱40.00 – ₱80.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["seizure disorders", "panic disorder", "anxiety", "sleep disorders (off-label)"],
        "dosage_adult": "As prescribed by physician. Dose varies; typical starting 0.5 mg twice daily.",
        "dosage_pediatric": "As prescribed by pediatric neurologist.",
        "intake_instructions": "Take as directed. Do not stop abruptly due to withdrawal and seizure risk.",
        "onset_of_action": "20–60 minutes",
        "side_effects_common": ["drowsiness", "dizziness", "fatigue", "memory problems", "unsteadiness"],
        "side_effects_serious": ["respiratory depression", "severe confusion", "suicidal thoughts", "dependence and withdrawal"],
        "contraindications": ["acute narrow-angle glaucoma", "severe liver disease", "sleep apnea", "hypersensitivity to benzodiazepines"],
        "drug_interactions": ["alcohol", "opioids", "other CNS depressants", "antihistamines"],
        "overdose_note": "Overdose causes severe sedation, respiratory depression, and coma. This is a medical emergency. Call 911.",
        "storage": "Store in a secure place. Controlled substance under RA 9165.",
        "pregnancy_category": "Category D — risk to fetus; consult OB-GYN immediately",
        "full_text": "Clonazepam (Rivotril) is a prescription controlled benzodiazepine for seizures and panic disorder. Strictly regulated under RA 9165."
    },
    {
        "drug_id": "PH-RX-016",
        "generic_name": "Tramadol",
        "drug_class": "Opioid Analgesic (Controlled Substance)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Tramal", "manufacturer": "Grunenthal", "form": "50mg capsule"},
            {"brand": "Ultram", "manufacturer": "Janssen", "form": "50mg tablet"},
            {"brand": "Tramadol Generic", "manufacturer": "Various", "form": "50mg capsule"}
        ],
        "ph_price_estimates": {
            "generic_per_capsule": "₱10.00 – ₱20.00",
            "tramal_per_capsule": "₱30.00 – ₱60.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["moderate to moderately severe pain"],
        "dosage_adult": "As prescribed by physician. Typical: 50–100 mg every 4–6 hours as needed. Maximum: 400 mg/day.",
        "dosage_pediatric": "Not generally recommended for children.",
        "intake_instructions": "Take with or without food. Do not crush extended-release formulations.",
        "onset_of_action": "1 hour",
        "side_effects_common": ["nausea", "dizziness", "constipation", "drowsiness", "headache"],
        "side_effects_serious": ["respiratory depression", "seizures", "serotonin syndrome", "severe hypotension", "addiction"],
        "contraindications": ["respiratory depression", "acute asthma", "MAOI use within 14 days", "suicidal risk", "history of substance abuse"],
        "drug_interactions": ["alcohol", "other opioids", "benzodiazepines", "SSRIs/SNRIs", "MAOIs"],
        "overdose_note": "Overdose causes respiratory depression, sedation, and death. This is a medical emergency. Call 911 immediately.",
        "storage": "Store in a secure place. Controlled substance under RA 9165.",
        "pregnancy_category": "Category C — avoid in pregnancy if possible; consult OB-GYN",
        "full_text": "Tramadol (Tramal, Ultram) is a prescription controlled opioid analgesic. Strictly regulated under RA 9165."
    },
    {
        "drug_id": "PH-RX-017",
        "generic_name": "Insulin Human Regular",
        "drug_class": "Antidiabetic Hormone (Injectable)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Humulin R", "manufacturer": "Eli Lilly", "form": "100 IU/mL vial / pen"},
            {"brand": "Novolin R", "manufacturer": "Novo Nordisk", "form": "100 IU/mL vial"},
            {"brand": "Insulin Human Regular Generic", "manufacturer": "Various", "form": "100 IU/mL vial"}
        ],
        "ph_price_estimates": {
            "generic_per_vial": "₱400.00 – ₱700.00",
            "humulin_per_vial": "₱800.00 – ₱1,500.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["Type 1 Diabetes", "Type 2 Diabetes (when oral agents insufficient)", "gestational diabetes", "diabetic ketoacidosis"],
        "dosage_adult": "As prescribed by physician. Dose is highly individualized based on blood glucose monitoring.",
        "dosage_pediatric": "As prescribed by pediatric endocrinologist.",
        "intake_instructions": "Subcutaneous injection as taught by healthcare provider. Rotate injection sites. Monitor blood sugar regularly.",
        "onset_of_action": "30 minutes (Regular insulin)",
        "side_effects_common": ["hypoglycemia", "weight gain", "injection site reactions", "lipodystrophy"],
        "side_effects_serious": ["severe hypoglycemia (unconsciousness, seizures)", "allergic reaction", "hypokalemia"],
        "contraindications": ["hypoglycemia", "hypersensitivity to insulin or excipients"],
        "drug_interactions": ["beta-blockers (mask hypoglycemia symptoms)", "corticosteroids", "thyroid hormones", "alcohol"],
        "overdose_note": "Insulin overdose causes severe hypoglycemia and can be fatal. Consume fast-acting sugar and seek emergency care immediately.",
        "storage": "Unopened: refrigerate 2–8°C. Opened vials/pen: room temperature up to 28°C for 28 days. Do not freeze.",
        "pregnancy_category": "Category B — insulin is standard treatment in pregnancy; consult OB-GYN",
        "full_text": "Insulin Human Regular (Humulin R, Novolin R) is a prescription injectable antidiabetic. Requires a doctor's prescription and injection training."
    },
    {
        "drug_id": "PH-RX-018",
        "generic_name": "Glimepiride",
        "drug_class": "Sulfonylurea Antidiabetic",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Amaryl", "manufacturer": "Sanofi", "form": "1mg / 2mg / 4mg tablet"},
            {"brand": "Glimepiride Generic", "manufacturer": "Various", "form": "2mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱8.00 – ₱18.00",
            "amaryl_per_tablet": "₱25.00 – ₱50.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["Type 2 Diabetes Mellitus"],
        "dosage_adult": "As prescribed by physician. Typical starting: 1–2 mg once daily with breakfast.",
        "dosage_pediatric": "Not recommended for children.",
        "intake_instructions": "Take with breakfast. Do not skip meals to avoid hypoglycemia.",
        "onset_of_action": "2–3 hours",
        "side_effects_common": ["hypoglycemia", "weight gain", "dizziness", "headache"],
        "side_effects_serious": ["severe hypoglycemia", "hemolytic anemia (in G6PD deficiency)", "allergic reaction"],
        "contraindications": ["Type 1 Diabetes", "diabetic ketoacidosis", "severe kidney or liver disease", "sulfonamide allergy"],
        "drug_interactions": ["alcohol (disulfiram-like reaction and hypoglycemia)", "beta-blockers", "NSAIDs", "warfarin"],
        "overdose_note": "Overdose causes severe hypoglycemia. Consume sugar and seek emergency care.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category C — consult OB-GYN; insulin preferred in pregnancy",
        "full_text": "Glimepiride (Amaryl) is a prescription sulfonylurea for Type 2 Diabetes. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-019",
        "generic_name": "Pantoprazole",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Protonix", "manufacturer": "Wyeth/Pfizer", "form": "40mg tablet / IV"},
            {"brand": "Pantoloc", "manufacturer": "Takeda", "form": "40mg tablet"},
            {"brand": "Pantoprazole Generic", "manufacturer": "Various", "form": "40mg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱10.00 – ₱20.00",
            "protonix_per_tablet": "₱30.00 – ₱60.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["GERD", "peptic ulcer disease", "Zollinger-Ellison syndrome", "erosive esophagitis"],
        "dosage_adult": "As prescribed by physician. Typical: 40 mg once daily before breakfast.",
        "dosage_pediatric": "As prescribed by pediatrician.",
        "intake_instructions": "Take 30 minutes before breakfast. Swallow whole; do not crush.",
        "onset_of_action": "2 hours",
        "side_effects_common": ["headache", "diarrhea", "nausea", "abdominal pain"],
        "side_effects_serious": ["C. difficile infection", "low magnesium (long-term)", "bone fractures (long-term)", "vitamin B12 deficiency (long-term)"],
        "contraindications": ["hypersensitivity to pantoprazole"],
        "drug_interactions": ["atazanavir", "ketoconazole", "warfarin", "methotrexate"],
        "overdose_note": "Overdose symptoms are usually mild. Seek medical advice.",
        "storage": "Store below 30°C.",
        "pregnancy_category": "Category B — consult OB-GYN",
        "full_text": "Pantoprazole (Protonix, Pantoloc) is a prescription PPI for GERD and ulcers. Requires a doctor's prescription."
    },
    {
        "drug_id": "PH-RX-020",
        "generic_name": "Levothyroxine",
        "drug_class": "Thyroid Hormone Replacement",
        "rx_status": "Rx",
        "fda_ph_registered": True,
        "ph_brands": [
            {"brand": "Synthroid", "manufacturer": "Abbott", "form": "50mcg / 100mcg tablet"},
            {"brand": "Euthyrox", "manufacturer": "Merck", "form": "50mcg / 100mcg tablet"},
            {"brand": "Levothyroxine Generic", "manufacturer": "Various", "form": "100mcg tablet"}
        ],
        "ph_price_estimates": {
            "generic_per_tablet": "₱5.00 – ₱12.00",
            "synthroid_per_tablet": "₱15.00 – ₱35.00",
            "source": "Mercury Drug / Generics Pharmacy (2024 estimate)"
        },
        "indications": ["hypothyroidism", "goiter", "thyroid hormone replacement after thyroidectomy"],
        "dosage_adult": "As prescribed by physician. Typical starting: 25–50 mcg daily on empty stomach.",
        "dosage_pediatric": "As prescribed by pediatric endocrinologist.",
        "intake_instructions": "Take on an empty stomach 30–60 minutes before breakfast. Separate from calcium, iron, and antacids by 4 hours.",
        "onset_of_action": "Days to weeks for clinical effect",
        "side_effects_common": ["weight loss", "tremor", "headache", "insomnia", "increased appetite"],
        "side_effects_serious": ["chest pain", "irregular heartbeat", "osteoporosis (over-replacement)", "thyrotoxicosis"],
        "contraindications": ["untreated adrenal insufficiency", "thyrotoxicosis", "acute myocardial infarction"],
        "drug_interactions": ["iron", "calcium", "antacids", "cholestyramine", "warfarin", "antidiabetic medications"],
        "overdose_note": "Overdose causes symptoms of hyperthyroidism: chest pain, irregular heartbeat, confusion. Seek emergency care.",
        "storage": "Store below 30°C. Protect from light and moisture.",
        "pregnancy_category": "Category A — essential in pregnancy; dose often increases; consult OB-GYN",
        "full_text": "Levothyroxine (Synthroid, Euthyrox) is a prescription thyroid hormone replacement. Requires a doctor's prescription."
    }
]


def generate_drug_database(output_path: str = "data/ph_drug_database.jsonl") -> None:
    """
    ================================================================================
    Generate the Philippine Drug Reference Database as a JSONL file.
    ================================================================================
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for record in MASTER_DRUGS:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    
    print(f"[SUCCESS] Generated {output_path} with {len(MASTER_DRUGS)} drug records.")
    print(f"          OTC: {sum(1 for d in MASTER_DRUGS if d['rx_status'] == 'OTC')}")
    print(f"          Rx:  {sum(1 for d in MASTER_DRUGS if d['rx_status'] == 'Rx')}")


if __name__ == "__main__":
    generate_drug_database()

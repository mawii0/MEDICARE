"""
================================================================================
PHARMABOT PH — Information Retrieval Layer (BM25)
================================================================================
Builds a BM25 index over the Philippine Drug Reference Database and provides
context retrieval for grounding LLM responses.
================================================================================
"""

import sys, os
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import json
from typing import List, Dict, Any, Tuple

from rank_bm25 import BM25Okapi
from src.preprocess import preprocess_for_classical_ml, translate_taglish_symptoms
from src.ph_drug_map import normalize_ph_drug_names

# ------------------------------------------------------------------------------
# RETRIEVAL ENGINE
# ------------------------------------------------------------------------------
class DrugRetrievalEngine:
    """
    ================================================================================
    BM25-based retrieval over the PH drug database.
    ================================================================================
    """

    def __init__(self, drug_db_path: str = "data/ph_drug_database.jsonl"):
        """
        ================================================================================
        Initialize the retrieval engine by loading records and building the BM25 index.
        ================================================================================
        """
        self.records: List[Dict[str, Any]] = []
        with open(drug_db_path, "r", encoding="utf-8") as f:
            for line in f:
                self.records.append(json.loads(line))

        # Build BM25 corpus from preprocessed full_text fields
        self.corpus_tokens = [
            preprocess_for_classical_ml(record.get("full_text", ""))
            for record in self.records
        ]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"[INFO] BM25 index built over {len(self.records)} drug records.")

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        rx_only: bool = False,
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        ================================================================================
        Retrieve top-k drug records matching the query.
        ================================================================================
        Args:
            query: Raw user query string.
            top_k: Number of records to retrieve.
            rx_only: If True, restrict results to Rx records only.

        Returns:
            (context_string, matched_records_list)
        ================================================================================
        """
        # Translate Taglish symptoms, normalize brand names, and preprocess
        query_translated = translate_taglish_symptoms(query)
        normalized_query = normalize_ph_drug_names(query_translated)
        q_tokens = preprocess_for_classical_ml(normalized_query)

        scores = self.bm25.get_scores(q_tokens)

        if rx_only:
            scores = [
                s if self.records[i]["rx_status"] == "Rx" else 0.0
                for i, s in enumerate(scores)
            ]

        # Get top-k indices sorted by score descending
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        matched = [self.records[i] for i in top_idx if scores[i] > 0]

        # Build context string for LLM prompt injection
        context_parts = []
        for rec in matched:
            brands = ", ".join(b["brand"] for b in rec.get("ph_brands", []))
            prices = rec.get("ph_price_estimates", {})
            generic_price = prices.get("generic_per_tablet", "N/A")
            branded_price = prices.get("branded_per_tablet", "N/A")
            # Try to find a branded price key
            for k, v in prices.items():
                if "generic" in k:
                    generic_price = v
                elif "branded" in k or any(b["brand"].lower() in k for b in rec.get("ph_brands", [])):
                    branded_price = v

            indications = ", ".join(rec.get("indications", []))
            side_effects = ", ".join(rec.get("side_effects_common", []))
            part = (
                f"Drug: {rec['generic_name']} ({brands}) | {rec['rx_status']}\n"
                f"Class: {rec.get('drug_class', 'N/A')}\n"
                f"Uses: {indications}\n"
                f"Side Effects: {side_effects}\n"
                f"Price: Generic {generic_price}, Branded {branded_price}\n"
            )
            context_parts.append(part)

        context = "\n---\n".join(context_parts) if context_parts else "No matching drug records found."
        return context, matched

    def get_record_by_generic(self, generic_name: str) -> Dict[str, Any] | None:
        """
        ================================================================================
        Exact lookup by generic name (case-insensitive).
        ================================================================================
        """
        for rec in self.records:
            if rec["generic_name"].lower() == generic_name.lower():
                return rec
        return None


# ------------------------------------------------------------------------------
# SIMPLE FUNCTION INTERFACE (for notebook demos)
# ------------------------------------------------------------------------------
def retrieve_drug_context(
    query: str,
    top_k: int = 3,
    rx_only: bool = False,
    drug_db_path: str = "data/ph_drug_database.jsonl",
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    ================================================================================
    Stateless wrapper for quick retrieval without instantiating the class manually.
    ================================================================================
    """
    engine = DrugRetrievalEngine(drug_db_path)
    return engine.retrieve(query, top_k=top_k, rx_only=rx_only)


if __name__ == "__main__":
    # Quick sanity demo
    demo_queries = [
        "What can I take for headache?",
        "How much is Amoxicillin?",
        "Tell me about Ventolin",
    ]
    engine = DrugRetrievalEngine()
    for q in demo_queries:
        ctx, recs = engine.retrieve(q, top_k=2)
        print("=" * 70)
        print(f"QUERY: {q}")
        print("-" * 70)
        safe_ctx = ctx[:500].replace(chr(0x20b1), "PHP")
        print(safe_ctx + "...")
        print(f"[MATCHED {len(recs)} RECORDS]\n")

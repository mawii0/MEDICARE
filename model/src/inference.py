"""
Pharmacare — End-to-End Inference Pipeline (Reusable Module)
================================================================
Lightweight importable version for api.py and other consumers.
"""

import os
import re
import torch
from typing import Dict, Any

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from src.guardrails import (
    route_query, check_emergency, get_emergency_response,
    enforce_rx_note, append_disclaimer, ClassifierInterface,
)
from src.retrieval import DrugRetrievalEngine
from src.preprocess import format_chat_prompt
from src.build_dataset import build_answer, build_structured_answer, format_structured_to_markdown

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
ADAPTER_PATH = "models/pharmacare_lora"
DRUG_DB_PATH = "data/ph_drug_database.jsonl"

# Training-data artifacts that must be stripped if the model hallucinates them
_HALLUCINATION_PATTERNS = [
    r"Hi welcome to Chat Doctor.*",
    r"I have gone through your question carefully.*",
    r"Hope this answers your question.*",
    r"Please do not hesitate to write back.*",
    r"Human:.*",
    r"User\d+ answered \d{4}-\d{2}-\d{2}\..*",
    r"The adult patient was diagnosed with.*",
    r"The best course of action would be to prescribe.*",
]


def _clean_hallucinations(text: str) -> str:
    """Strip known training-data artifacts and unwanted tokens from model output."""
    for pattern in _HALLUCINATION_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
    # Strip special tokens and anything after them
    text = re.split(r"<\|endoftext\|>", text)[0]
    # Remove CJK characters (Chinese/Japanese/Korean) that sometimes leak in
    text = re.sub(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]", "", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class PharmacareInference:
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        adapter_path: str = ADAPTER_PATH,
        drug_db_path: str = DRUG_DB_PATH,
        model_dir: str = "models",
    ):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Using device: {self.device}")

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
        self.tokenizer = tokenizer

        print(f"[INFO] Loading base model: {model_name}")
        if self.device == "cuda":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
            )
            base_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )
        else:
            print("[INFO] No CUDA detected — loading model on CPU (float32, slower)")
            base_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float32,
                trust_remote_code=True,
            )

        if os.path.isdir(adapter_path):
            print(f"[INFO] Loading LoRA adapter: {adapter_path}")
            self.model = PeftModel.from_pretrained(base_model, adapter_path)
        else:
            print(f"[WARN] Adapter not found at {adapter_path}. Using base model only.")
            self.model = base_model
        self.model.eval()

        print(f"[INFO] Loading BM25 retrieval engine...")
        self.retrieval = DrugRetrievalEngine(drug_db_path)

        print(f"[INFO] Loading classifiers...")
        try:
            self.classifier = ClassifierInterface(model_dir)
        except Exception as e:
            print(f"[WARN] Could not load classifiers: {e}")
            self.classifier = None

        print("[INFO] Pharmacare inference engine ready.\n")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 250,
        temperature: float = 0.15,
        top_p: float = 0.85,
        top_k: int = 40,
        repetition_penalty: float = 1.25,
    ) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=768)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repetition_penalty=repetition_penalty,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        decoded = self.tokenizer.decode(output_ids[0], skip_special_tokens=False)
        marker = "<|assistant|>\n"
        if marker in decoded:
            # Take the last assistant turn (model may echo prior turns)
            response = decoded.split(marker)[-1].strip()
            # Strip trailing </s> and other special tokens
            for tok_str in ["</s>", "<|endoftext|>", "</s>\n"]:
                if response.endswith(tok_str):
                    response = response[: -len(tok_str)].strip()
            return response
        return decoded.strip()

    def chat(self, raw_query: str) -> Dict[str, Any]:
        routing = route_query(raw_query, classifier=self.classifier)
        lang = routing["language"]

        if routing["emergency"]:
            structured = build_structured_answer("emergency_escalation", [], lang)
            final_response = get_emergency_response(lang)
            return {
                "query": raw_query, "language": lang, "emergency": True,
                "intent": "emergency_escalation", "rx_flag": False,
                "retrieved_context": "", "response": final_response,
                "structured": structured,
            }

        rx_only_retrieval = routing["rx_flag"] or routing["intent"] == "rx_info_restricted"
        context, matched_records = self.retrieval.retrieve(raw_query, top_k=3, rx_only=rx_only_retrieval)

        # ------------------------------------------------------------------
        # If Rx-only retrieval is empty, retry without Rx restriction.
        # This handles Rx-classifier false positives on OTC queries.
        # ------------------------------------------------------------------
        if not matched_records and rx_only_retrieval:
            context, matched_records = self.retrieval.retrieve(raw_query, top_k=3, rx_only=False)

        # ------------------------------------------------------------------
        # HARD FALLBACK: if no drugs were retrieved, do NOT call the LLM.
        # ------------------------------------------------------------------
        if not matched_records:
            fallback = (
                "I'm sorry, I don't have specific information about that in my Philippine drug database. "
                "I can help with questions about the medicines listed in my reference, such as common OTC and Rx drugs available in the Philippines. "
                "If you're experiencing symptoms, please consult a licensed physician or pharmacist for proper advice."
            )
            structured = {"message": fallback, "advice": "Consult a licensed physician or pharmacist."}
            return {
                "query": raw_query, "language": lang, "emergency": False,
                "intent": routing["intent"], "rx_flag": routing["rx_flag"],
                "retrieved_context": context, "response": append_disclaimer(fallback, lang=lang),
                "structured": structured,
            }

        # ------------------------------------------------------------------
        # Deterministic structured answer generation from retrieved records.
        # ------------------------------------------------------------------
        structured = build_structured_answer(routing["intent"], matched_records, lang)
        markdown = format_structured_to_markdown(structured, lang)

        # Post-generation safety: strip artifacts and enforce Rx rules
        markdown = _clean_hallucinations(markdown)

        is_rx = any(r["rx_status"] == "Rx" for r in matched_records)
        is_controlled = any("controlled" in r.get("drug_class", "").lower() for r in matched_records)
        if is_rx or routing["rx_flag"]:
            markdown = enforce_rx_note(markdown, is_controlled=is_controlled, lang=lang)
        final_response = append_disclaimer(markdown, lang=lang)

        return {
            "query": raw_query, "language": lang, "emergency": False,
            "intent": routing["intent"], "rx_flag": routing["rx_flag"],
            "retrieved_context": context, "response": final_response,
            "structured": structured,
        }


# Singleton for stateless chat() convenience
_bot: PharmacareInference | None = None


def chat(raw_query: str) -> str:
    """Convenience wrapper that returns only the human-readable response string."""
    global _bot
    if _bot is None:
        _bot = PharmacareInference()
    result = _bot.chat(raw_query)
    return result["response"]


def chat_full(raw_query: str) -> Dict[str, Any]:
    """Convenience wrapper that returns the full response dict including structured JSON."""
    global _bot
    if _bot is None:
        _bot = PharmacareInference()
    return _bot.chat(raw_query)

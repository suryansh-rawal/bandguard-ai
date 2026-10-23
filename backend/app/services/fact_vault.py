import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings

def tokenize(text: str) -> set[str]:
    """Tokenize and normalize text into word stems/n-grams."""
    cleaned = re.sub(r'[^\w\s%.-]', ' ', text.lower())
    words = [w for w in cleaned.split() if len(w) > 1]
    return set(words)

class FactVault:
    def __init__(self, brand_kit_path: Optional[Path] = None):
        self.brand_kit_path = brand_kit_path or settings.BRAND_KIT_PATH
        self.facts: List[Dict[str, Any]] = []
        self.load_facts()

    def load_facts(self) -> None:
        """Load Fact Vault items from brand_kit.json."""
        if not self.brand_kit_path.exists():
            return

        try:
            with open(self.brand_kit_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.facts = data.get("fact_vault", [])
        except Exception as e:
            print(f"[FactVault] Warning: Failed to load fact vault: {e}")

    def find_best_match(self, claim_text: str) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Find the most relevant Fact Vault item for a given claim.
        Returns (fact_item, similarity_score).
        """
        if not self.facts:
            return None, 0.0

        claim_tokens = tokenize(claim_text)
        if not claim_tokens:
            return None, 0.0

        best_fact = None
        best_score = 0.0

        for fact in self.facts:
            fact_tokens = tokenize(fact["statement"])
            keywords = {k.lower() for k in fact.get("keywords", [])}
            
            # Combine fact statement tokens and keywords
            all_target_tokens = fact_tokens.union(keywords)

            # Jaccard overlap
            intersection = claim_tokens.intersection(all_target_tokens)
            union = claim_tokens.union(all_target_tokens)
            jaccard = len(intersection) / len(union) if union else 0.0

            # Direct keyword match boost
            keyword_hits = sum(1 for kw in keywords if kw in claim_text.lower())
            keyword_boost = min(0.4, keyword_hits * 0.15)

            # Check if specific numbers match (e.g. 10,000, 99.95%, 42, 50ms)
            claim_numbers = set(re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', claim_text))
            fact_numbers = set(re.findall(r'\b\d+(?:[\.,]\d+)?%?\b', fact["statement"]))
            number_match = bool(claim_numbers.intersection(fact_numbers))
            number_boost = 0.25 if number_match else 0.0

            total_score = min(1.0, (jaccard * 0.5) + keyword_boost + number_boost)

            if total_score > best_score:
                best_score = total_score
                best_fact = fact

        return best_fact, round(best_score, 3)

    def get_all_sources(self) -> List[str]:
        """Return list of valid source strings and IDs for citation validation."""
        sources = []
        for f in self.facts:
            sources.append(f["source"])
            sources.append(f["id"])
            sources.append(f"Fact Vault: {f['id']}")
        return sources

fact_vault = FactVault()

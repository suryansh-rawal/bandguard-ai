import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
from app.core.config import settings

class CitationValidator:
    """
    K6: Citation Validation Service.
    Verifies that any finding emitted by AI or automated rules references a real,
    existing, authorized guideline or Fact Vault entry. Rejects hallucinated citations.
    """

    def __init__(self, brand_kit_path: Optional[Path] = None):
        self.brand_kit_path = brand_kit_path or settings.BRAND_KIT_PATH
        self.valid_source_ids: Set[str] = set()
        self.valid_source_names: Set[str] = set()
        self.load_valid_sources()

    def load_valid_sources(self) -> None:
        """Extract all known sources from brand kit."""
        # Built-in general sources
        self.valid_source_names = {
            "brand kit - glossary v1.2",
            "brand kit - glossary",
            "brand kit - tone guidelines",
            "brand kit",
            "fact vault",
            "fact vault verification",
        }
        self.valid_source_ids = {"fv-unverified", "general"}

        if not self.brand_kit_path.exists():
            return

        try:
            with open(self.brand_kit_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 1. Guidelines
            for tone in data.get("brand", {}).get("tone_principles", []):
                self.valid_source_ids.add(tone["id"].lower())
                self.valid_source_names.add(tone["name"].lower())

            # 2. Glossary
            glossary = data.get("glossary", {})
            for item in glossary.get("banned_terms", []) + glossary.get("preferred_terms", []):
                self.valid_source_ids.add(item["id"].lower())
                if "source" in item:
                    self.valid_source_names.add(item["source"].lower())

            # 3. Fact Vault
            for fact in data.get("fact_vault", []):
                self.valid_source_ids.add(fact["id"].lower())
                self.valid_source_names.add(fact["source"].lower())
                self.valid_source_names.add(f"fact vault: {fact['id']}".lower())

        except Exception as e:
            print(f"[CitationValidator] Warning: Failed to load valid sources: {e}")

    def is_valid_source(self, source: Optional[str], source_id: Optional[str]) -> bool:
        """Check if source name or ID is genuine."""
        if source_id and source_id.strip().lower() in self.valid_source_ids:
            return True

        if source:
            source_lower = source.strip().lower()
            if source_lower in self.valid_source_names:
                return True
            # Substring match against valid source names
            for valid in self.valid_source_names:
                if valid in source_lower or source_lower in valid:
                    return True

        return False

    def validate_issues(self, issues: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filters issues list. Returns (valid_issues, rejected_issues).
        Any finding whose source cannot be validated against brand records is rejected.
        """
        valid_issues = []
        rejected_issues = []

        for issue in issues:
            source = issue.get("source")
            source_id = issue.get("source_id")

            if self.is_valid_source(source, source_id):
                valid_issues.append(issue)
            else:
                rejected_issues.append(issue)

        return valid_issues, rejected_issues

citation_validator = CitationValidator()

import re
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import settings

class RulesEngine:
    def __init__(self, brand_kit_path: Optional[Path] = None):
        self.brand_kit_path = brand_kit_path or settings.BRAND_KIT_PATH
        self.banned_rules: List[Dict[str, Any]] = []
        self.preferred_rules: List[Dict[str, Any]] = []
        self.brand_name: str = "BrandGuard AI"
        self._compiled_banned: List[Dict[str, Any]] = []
        self._compiled_preferred: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self) -> None:
        """Load rules from brand_kit.json and compile regular expressions."""
        if not self.brand_kit_path.exists():
            return

        try:
            with open(self.brand_kit_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.brand_name = data.get("brand", {}).get("name", "BrandGuard AI")
            glossary = data.get("glossary", {})
            self.banned_rules = glossary.get("banned_terms", [])
            self.preferred_rules = glossary.get("preferred_terms", [])

            self._compiled_banned = []
            for item in self.banned_rules:
                patterns = item.get("patterns", [re.escape(item["term"])])
                compiled_patterns = []
                for p in patterns:
                    try:
                        # Ensure boundary if not already present
                        pattern_str = p if p.startswith("\\b") or p.startswith("(?") else f"\\b{p}\\b"
                        compiled_patterns.append(re.compile(pattern_str, re.IGNORECASE))
                    except re.error:
                        compiled_patterns.append(re.compile(re.escape(p), re.IGNORECASE))
                
                self._compiled_banned.append({
                    "meta": item,
                    "patterns": compiled_patterns
                })

            self._compiled_preferred = []
            for item in self.preferred_rules:
                patterns = item.get("patterns", [re.escape(item["term"])])
                compiled_patterns = []
                for p in patterns:
                    try:
                        pattern_str = p if p.startswith("\\b") or p.startswith("(?") else f"\\b{p}\\b"
                        compiled_patterns.append(re.compile(pattern_str, re.IGNORECASE))
                    except re.error:
                        compiled_patterns.append(re.compile(re.escape(p), re.IGNORECASE))
                
                self._compiled_preferred.append({
                    "meta": item,
                    "patterns": compiled_patterns
                })

        except Exception as e:
            print(f"[RulesEngine] Warning: Failed to load brand kit: {e}")

    def scan(self, text: str) -> List[Dict[str, Any]]:
        """
        Scan input text against banned terms and preferred terms.
        Returns list of detected issue dictionaries matching API contract.
        """
        issues: List[Dict[str, Any]] = []
        occupied_spans: List[tuple[int, int]] = []

        def overlaps(s: int, e: int) -> bool:
            return any(s < end and e > start for start, end in occupied_spans)

        # 1. Check Banned Terms
        for entry in self._compiled_banned:
            meta = entry["meta"]
            for regex in entry["patterns"]:
                for match in regex.finditer(text):
                    start, end = match.start(), match.end()
                    if overlaps(start, end):
                        continue
                    occupied_spans.append((start, end))
                    matched_str = match.group()
                    fix = meta.get("alternatives", [""])[0] if meta.get("alternatives") else None
                    issues.append({
                        "id": f"iss-ban-{len(issues)+1:03d}",
                        "type": "banned_term",
                        "severity": meta.get("severity", "critical"),
                        "matched_text": matched_str,
                        "start_offset": start,
                        "end_offset": end,
                        "reason": meta.get("reason", "Use of banned vocabulary"),
                        "suggested_fix": fix,
                        "source": meta.get("source", "Brand Kit - Glossary v1.2"),
                        "source_id": meta.get("id"),
                        "confidence": 1.0,
                        "intent_preserved": True
                    })

        # 2. Check Preferred Terms
        for entry in self._compiled_preferred:
            meta = entry["meta"]
            preferred = meta.get("preferred", "")
            for regex in entry["patterns"]:
                for match in regex.finditer(text):
                    start, end = match.start(), match.end()
                    matched_str = match.group()
                    # Skip if the matched text is already exactly the preferred spelling
                    if matched_str == preferred:
                        continue
                    if overlaps(start, end):
                        continue
                    occupied_spans.append((start, end))
                    issues.append({
                        "id": f"iss-pref-{len(issues)+1:03d}",
                        "type": "preferred_term",
                        "severity": meta.get("severity", "suggestion"),
                        "matched_text": matched_str,
                        "start_offset": start,
                        "end_offset": end,
                        "reason": meta.get("reason", f"Preferred brand term is '{preferred}'"),
                        "suggested_fix": preferred,
                        "source": meta.get("source", "Brand Kit - Glossary v1.2"),
                        "source_id": meta.get("id"),
                        "confidence": 1.0,
                        "intent_preserved": True
                    })

        # Sort issues by start_offset
        issues.sort(key=lambda x: x["start_offset"])
        return issues

rules_engine = RulesEngine()

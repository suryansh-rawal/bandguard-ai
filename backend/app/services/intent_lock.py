import re
from typing import Tuple

class IntentLock:
    """
    K7: Intent Lock Service.
    Verifies that a suggested fix preserves the original meaning and communicative intent
    of the flagged draft text, guarding against semantic drift or unintended negation.
    """

    def __init__(self):
        # Negation keywords to detect polarity shifts
        self.negation_words = {"not", "never", "no", "neither", "nor", "barely", "hardly", "none"}
        
        # Stopwords to filter out when checking semantic topic overlap
        self.stopwords = {
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
            "is", "are", "was", "were", "be", "been", "our", "we", "you", "your", "it"
        }

    def _get_content_words(self, text: str) -> set[str]:
        words = re.findall(r'[a-zA-Z0-9]+', text.lower())
        return {w for w in words if w not in self.stopwords and len(w) > 1}

    def verify_fix(self, original_text: str, suggested_fix: str) -> Tuple[bool, float, str]:
        """
        Verify if suggested_fix preserves the intent of original_text.
        Returns (is_preserved: bool, score: float, note: str).
        """
        if not suggested_fix or not original_text:
            return True, 1.0, "Empty or unchanged fix"

        orig_lower = original_text.lower()
        fix_lower = suggested_fix.lower()

        # 1. Check for abrupt negation flip
        orig_has_neg = any(w in orig_lower.split() for w in self.negation_words)
        fix_has_neg = any(w in fix_lower.split() for w in self.negation_words)

        if orig_has_neg != fix_has_neg:
            # Polarity inversion detected
            return False, 0.3, "Fix reverses polarity or introduces unexpected negation"

        # 2. Check semantic topic overlap
        orig_words = self._get_content_words(orig_lower)
        fix_words = self._get_content_words(fix_lower)

        if not orig_words or not fix_words:
            return True, 0.8, "Short text, intent assumed preserved"

        common_words = orig_words.intersection(fix_words)
        overlap_ratio = len(common_words) / min(len(orig_words), len(fix_words))

        # Check for numeric consistency if both specify numbers
        orig_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', orig_lower))
        fix_nums = set(re.findall(r'\b\d+(?:\.\d+)?%?\b', fix_lower))

        # If numbers are modified (e.g. 100% -> 99.95%), that is intentional compliance correction,
        # but topic terms should still align (e.g. "uptime" in both).
        has_domain_anchor = any(term in orig_lower and term in fix_lower for term in [
            "uptime", "sla", "security", "teams", "latency", "scale", "certified", "compliance"
        ])

        if overlap_ratio >= 0.20 or has_domain_anchor:
            return True, max(0.75, overlap_ratio), "Intent and core topic preserved"
        
        # If very low overlap and no common domain anchor, flag for reviewer review
        return False, overlap_ratio, "Significant semantic divergence between original and fix"

intent_lock = IntentLock()

from datetime import date, datetime
from typing import List, Dict, Any, Optional
from app.services.claim_extractor import claim_extractor
from app.services.fact_vault import fact_vault

class ClaimPassport:
    """
    Advanced Claim Verification Engine (Claim Passport).
    Monitors claims in draft content against the Fact Vault lifecycle,
    flagging expired facts and unverified quantitative assertions.
    """

    def __init__(self, reference_date: Optional[date] = None):
        # Default to current date (or 2026-10-23 for competition context)
        self.reference_date = reference_date or date.today()

    def evaluate_claims(self, text: str) -> List[Dict[str, Any]]:
        """
        Analyze all claims extracted from text, cross-referencing with Fact Vault
        to identify expired facts and unverified claims.
        """
        issues: List[Dict[str, Any]] = []
        claims = claim_extractor.extract_claims(text)
        today_str = self.reference_date.isoformat()

        for idx, claim in enumerate(claims):
            best_fact, score = fact_vault.find_best_match(claim["text"])

            if best_fact and score >= 0.40:
                expires_on = best_fact.get("expires_on")
                if expires_on and expires_on < today_str:
                    # Expired fact detected!
                    issues.append({
                        "id": f"iss-exp-{idx+1:03d}",
                        "type": "expired_fact",
                        "severity": "warning",
                        "matched_text": claim["text"],
                        "start_offset": claim["start_offset"],
                        "end_offset": claim["end_offset"],
                        "reason": f"Claim references '{best_fact['statement']}' (Fact Vault {best_fact['id']}), but its verification expired on {expires_on} (Claim Passport warning).",
                        "suggested_fix": f"Refresh metric with latest audited figures to replace expired {best_fact['id']}.",
                        "source": f"Fact Vault: {best_fact['id']}",
                        "source_id": best_fact["id"],
                        "confidence": score,
                        "intent_preserved": True
                    })
            elif score < 0.25 and len(claim.get("indicators", [])) >= 2:
                # High-specificity claim with zero backing in Fact Vault
                issues.append({
                    "id": f"iss-unver-{idx+1:03d}",
                    "type": "unverified_claim",
                    "severity": "warning",
                    "matched_text": claim["text"],
                    "start_offset": claim["start_offset"],
                    "end_offset": claim["end_offset"],
                    "reason": "Specific numerical or SLA claim detected with no approved matching record in Fact Vault.",
                    "suggested_fix": "Substantiate claim with official audit/performance data or register it in Fact Vault.",
                    "source": "Fact Vault Verification",
                    "source_id": "FV-UNVERIFIED",
                    "confidence": 0.85,
                    "intent_preserved": True
                })

        return issues

claim_passport = ClaimPassport()

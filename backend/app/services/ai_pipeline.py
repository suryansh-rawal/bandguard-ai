import json
import logging
import time
from typing import List, Dict, Any, Tuple
import httpx
from app.core.config import settings
from app.services.rules_engine import rules_engine
from app.services.safe_scan import safe_scan
from app.services.claim_passport import claim_passport
from app.services.citation_validator import citation_validator
from app.services.intent_lock import intent_lock

logger = logging.getLogger("BrandGuard.AIPipeline")

class AIPipeline:
    """
    K5 & K13: AI Analysis Pipeline with Anthropic Claude integration
    and guaranteed zero-downtime deterministic fallback.
    """

    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = settings.CLAUDE_MODEL
        self.gemini_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL
        self.timeout = settings.AI_TIMEOUT_SECONDS

    def _build_system_prompt(self) -> str:
        return (
            "You are BrandGuard AI, an enterprise compliance and brand safety auditor. "
            "Analyze the provided text against brand guidelines, tone, and factual claims.\n\n"
            "Active Brand Tone Principles:\n"
            "- TONE-01: Empowering & Professional (Clear, confident, no arrogance or colloquial slang)\n"
            "- TONE-02: Factual & Evidentiary (No unverified absolutes, hyperbole, or unsubstantiated guarantees)\n"
            "- TONE-03: Transparent & Precise (Accurate technical terminology)\n\n"
            "OUTPUT FORMAT:\n"
            "You MUST return ONLY a valid JSON array of objects. Do not include markdown codeblocks or preamble.\n"
            "Each object must have:\n"
            "- 'matched_text': exact substring from the text that violates guidelines\n"
            "- 'type': 'tone_mismatch' | 'regulatory_risk' | 'unverified_claim'\n"
            "- 'severity': 'critical' | 'warning' | 'suggestion'\n"
            "- 'reason': clear explanation citing the guideline\n"
            "- 'suggested_fix': brand-aligned alternative\n"
            "- 'source': valid guideline title or Fact Vault reference\n"
            "- 'source_id': guideline or fact ID (e.g. 'TONE-01', 'TONE-02', 'TONE-03')\n"
            "- 'confidence': float between 0.0 and 1.0\n\n"
            "CRITICAL: If the text conforms well, return an empty array []. "
            "Only cite real, existing brand principles (TONE-01, TONE-02, TONE-03)."
        )

    async def _call_claude_api(self, prompt_text: str) -> List[Dict[str, Any]]:
        """Call Anthropic Messages API with structured system prompt."""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not configured.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        payload = {
            "model": self.model,
            "max_tokens": 1500,
            "temperature": 0.0,
            "system": self._build_system_prompt(),
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze the following draft text:\n\n{prompt_text}"
                }
            ]
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            # Extract assistant response text
            content_blocks = data.get("content", [])
            reply_text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
            
            # Clean possible markdown wrapping
            reply_clean = reply_text.strip()
            if reply_clean.startswith("```json"):
                reply_clean = reply_clean[7:]
            if reply_clean.startswith("```"):
                reply_clean = reply_clean[3:]
            if reply_clean.endswith("```"):
                reply_clean = reply_clean[:-3]
            reply_clean = reply_clean.strip()

            parsed = json.loads(reply_clean)
            if isinstance(parsed, list):
                return parsed
            return []

    async def _call_gemini_api(self, prompt_text: str) -> List[Dict[str, Any]]:
        """Call Google Gemini generateContent API (Free tier from Google AI Studio)."""
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_key}"
        headers = {"content-type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": self._build_system_prompt()}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": f"Analyze the following draft text:\n\n{prompt_text}"}]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "response_mime_type": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if not candidates:
                return []

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            reply_text = "".join(p.get("text", "") for p in parts)

            reply_clean = reply_text.strip()
            if reply_clean.startswith("```json"):
                reply_clean = reply_clean[7:]
            if reply_clean.startswith("```"):
                reply_clean = reply_clean[3:]
            if reply_clean.endswith("```"):
                reply_clean = reply_clean[:-3]
            reply_clean = reply_clean.strip()

            parsed = json.loads(reply_clean)
            if isinstance(parsed, list):
                return parsed
            return []

    async def analyze(self, text: str, skip_ai: bool = False) -> Tuple[List[Dict[str, Any]], bool, bool]:
        """
        Run end-to-end analysis on draft text.
        Returns: (issues, ai_used, safe_scan_applied)
        Guaranteed fallback: If AI fails or skip_ai=True, returns deterministic issues.
        """
        # Step 1: Run deterministic Rules Engine (banned terms, preferred terms)
        rule_issues = rules_engine.scan(text)

        # Step 2: Run Claim Passport (expired facts, unverified assertions)
        passport_issues = claim_passport.evaluate_claims(text)

        # Merge baseline deterministic issues
        combined_issues = list(rule_issues)
        occupied_spans = [(i["start_offset"], i["end_offset"]) for i in rule_issues]

        for p_issue in passport_issues:
            s, e = p_issue["start_offset"], p_issue["end_offset"]
            # Avoid duplicate flagging if already flagged by banned rules
            if not any(s < end and e > start for start, end in occupied_spans):
                combined_issues.append(p_issue)
                occupied_spans.append((s, e))

        ai_used = False
        safe_scan_applied = False

        if not skip_ai and (self.api_key or self.gemini_key):
            try:
                # Step 3: K8 Safe Scan PII Masking
                scan_res = safe_scan.mask(text)
                safe_scan_applied = scan_res.applied

                # Step 4: K5 LLM API call (Claude or free Gemini)
                if self.api_key:
                    raw_ai_issues = await self._call_claude_api(scan_res.masked_text)
                else:
                    raw_ai_issues = await self._call_gemini_api(scan_res.masked_text)
                ai_used = True

                # Step 5: Post-process AI findings
                for raw in raw_ai_issues:
                    matched = raw.get("matched_text", "")
                    # Unmask tokens in matched text and fix
                    if safe_scan_applied:
                        matched = safe_scan.unmask(matched, scan_res.replacements)
                        if "suggested_fix" in raw and raw["suggested_fix"]:
                            raw["suggested_fix"] = safe_scan.unmask(raw["suggested_fix"], scan_res.replacements)

                    # Locate offset in original text
                    start_pos = text.lower().find(matched.lower()) if matched else -1
                    if start_pos == -1:
                        continue
                    end_pos = start_pos + len(matched)

                    # Check span overlap
                    if any(start_pos < end and end_pos > start for start, end in occupied_spans):
                        continue

                    # K6: Citation Validation
                    is_valid = citation_validator.is_valid_source(raw.get("source"), raw.get("source_id"))
                    if not is_valid:
                        # Reject hallucinated citation!
                        logger.warning(f"Rejected AI issue due to invalid source: {raw.get('source')}")
                        continue

                    # K7: Intent Lock check on suggested fix
                    is_preserved, _, _ = intent_lock.verify_fix(matched, raw.get("suggested_fix", ""))

                    issue_item = {
                        "id": f"iss-ai-{len(combined_issues)+1:03d}",
                        "type": raw.get("type", "tone_mismatch"),
                        "severity": raw.get("severity", "suggestion"),
                        "matched_text": matched,
                        "start_offset": start_pos,
                        "end_offset": end_pos,
                        "reason": raw.get("reason", "Brand tone non-compliance"),
                        "suggested_fix": raw.get("suggested_fix"),
                        "source": raw.get("source", "Brand Kit - Tone Guidelines"),
                        "source_id": raw.get("source_id", "TONE-01"),
                        "confidence": float(raw.get("confidence", 0.9)),
                        "intent_preserved": is_preserved
                    }
                    combined_issues.append(issue_item)
                    occupied_spans.append((start_pos, end_pos))

            except Exception as e:
                # K13: AI Fallback Guarantee - Never fail, return rule results with ai_used=False
                logger.warning(f"[AIPipeline] AI analysis unavailable or failed: {e}. Gracefully falling back to deterministic rules.")
                ai_used = False

        # Final K6 Citation Validation pass across all combined issues
        valid_issues, _ = citation_validator.validate_issues(combined_issues)
        valid_issues.sort(key=lambda x: x["start_offset"])

        return valid_issues, ai_used, safe_scan_applied

ai_pipeline = AIPipeline()

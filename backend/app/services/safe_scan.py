import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass, field

@dataclass
class SafeScanResult:
    masked_text: str
    original_text: str
    applied: bool
    replacements: List[Dict[str, Any]] = field(default_factory=list)

class SafeScan:
    def __init__(self):
        # Email pattern
        self.email_regex = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        )
        # Phone pattern (International, US, Indian, hyphens/spaces/parentheses)
        self.phone_regex = re.compile(
            r'(?:(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}\b)'
        )
        # Name heuristic: names preceded by greeting/role/preposition or titles
        self.name_prefix_regex = re.compile(
            r'\b(?:Mr\.|Ms\.|Mrs\.|Dr\.|Contact|Reach out to|Spokesperson|Author|By)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
        )

    def mask(self, text: str) -> SafeScanResult:
        """
        Mask email addresses, phone numbers, and personal names with redaction tokens.
        """
        replacements = []
        masked_text = text

        # 1. Mask Emails
        def email_repl(match):
            original = match.group()
            token = f"[EMAIL_REDACTED_{len(replacements) + 1}]"
            replacements.append({
                "token": token,
                "original": original,
                "type": "email",
                "start": match.start(),
                "end": match.end()
            })
            return token

        masked_text = self.email_regex.sub(email_repl, masked_text)

        # 2. Mask Phone numbers (only if contains at least 7 digits to avoid matching short numbers like 2026 or 100%)
        def phone_repl(match):
            original = match.group().strip()
            digits_only = re.sub(r'\D', '', original)
            if len(digits_only) >= 7 and not original.endswith("%"):
                token = f"[PHONE_REDACTED_{len(replacements) + 1}]"
                replacements.append({
                    "token": token,
                    "original": original,
                    "type": "phone",
                    "start": match.start(),
                    "end": match.end()
                })
                return token
            return original

        masked_text = self.phone_regex.sub(phone_repl, masked_text)

        # 3. Mask Names (following prefix keywords)
        def name_repl(match):
            prefix_full = match.group()
            name_part = match.group(1)
            token = f"[NAME_REDACTED_{len(replacements) + 1}]"
            replacements.append({
                "token": token,
                "original": name_part,
                "type": "name",
                "start": match.start(1),
                "end": match.end(1)
            })
            return prefix_full.replace(name_part, token)

        masked_text = self.name_prefix_regex.sub(name_repl, masked_text)

        return SafeScanResult(
            masked_text=masked_text,
            original_text=text,
            applied=len(replacements) > 0,
            replacements=replacements
        )

    def unmask(self, text: str, replacements: List[Dict[str, Any]]) -> str:
        """Restore redacted tokens back to original values."""
        unmasked = text
        for item in replacements:
            unmasked = unmasked.replace(item["token"], item["original"])
        return unmasked

safe_scan = SafeScan()

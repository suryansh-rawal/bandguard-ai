import re
from typing import List, Dict, Any

class ClaimExtractor:
    def __init__(self):
        # Triggers that indicate quantitative or verifiable assertions
        self.claim_indicators = [
            r'\b\d+(?:\.\d+)?%',                    # Percentages (99.95%, 100%)
            r'\b\d{1,3}(?:,\d{3})+\b',             # Formatted numbers (10,000)
            r'\b\d+\s*(?:ms|seconds|minutes|hours)\b', # Latency or duration (50ms)
            r'\b(?:ISO\s*27001|SOC\s*2|GDPR|HIPAA|AES-?\d+|TLS\s*\d\.\d)\b', # Standards
            r'\b(?:uptime|SLA|guaranteed|certified|audited|retention|availability zones)\b',
            r'\b(?:over|more than|exceeding)\s+\d+', # Over 10,000
        ]
        self.combined_regex = re.compile('|'.join(self.claim_indicators), re.IGNORECASE)

    def extract_claims(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract sentences or clauses from text that assert measurable or verifiable claims.
        """
        claims = []
        # Split text into sentences while tracking offsets
        sentence_regex = re.compile(r'([^.!?\n]+[.!?\n]?)')
        
        for match in sentence_regex.finditer(text):
            sentence = match.group().strip()
            if not sentence or len(sentence) < 10:
                continue

            # Check if this sentence contains any claim indicators
            if self.combined_regex.search(sentence):
                claims.append({
                    "text": sentence,
                    "start_offset": match.start(),
                    "end_offset": match.end(),
                    "indicators": [m.group() for m in self.combined_regex.finditer(sentence)]
                })

        return claims

claim_extractor = ClaimExtractor()

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Draft text content to analyze")
    document_id: Optional[str] = Field(default=None, description="Optional linked document ID")
    skip_ai: bool = Field(default=False, description="Whether to bypass LLM and use rule-only analysis")
    brand_id: Optional[str] = Field(default="default", description="Brand configuration ID")

class IssueOut(BaseModel):
    id: str
    type: str  # banned_term, preferred_term, unverified_claim, expired_fact, tone_mismatch, regulatory_risk
    severity: str  # critical, warning, suggestion
    matched_text: str
    start_offset: int
    end_offset: int
    reason: str
    suggested_fix: Optional[str] = None
    source: Optional[str] = None
    source_id: Optional[str] = None
    confidence: float = 1.0
    intent_preserved: bool = True

    model_config = ConfigDict(from_attributes=True)

class SummaryOut(BaseModel):
    total_issues: int = 0
    critical: int = 0
    warning: int = 0
    suggestion: int = 0

class AnalyzeResponse(BaseModel):
    document_id: Optional[str] = None
    status: str = "completed"
    confidence_score: float = 100.0
    confidence_rating: str = "green"  # green, yellow, red
    ai_used: bool = False
    safe_scan_applied: bool = False
    processing_time_ms: float = 0.0
    summary: SummaryOut
    issues: List[IssueOut] = []

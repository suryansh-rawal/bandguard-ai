import time
import uuid
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, IssueOut, SummaryOut
from app.services.ai_pipeline import ai_pipeline
from app.services.confidence_router import confidence_router
from app.models.document import Document, AnalysisRecord, AnalysisIssue
from app.models.audit import AuditLog
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Brand Analysis"])

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    payload: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Core Brand Analysis Endpoint.
    Analyzes draft copy against Brand Kit rules, banned/preferred terms,
    Fact Vault assertions, and Claim Passport expiration checks.
    """
    t0 = time.perf_counter()

    # Step 1: Run analysis through AI & Rules Pipeline
    issues, ai_used, safe_scan_applied = await ai_pipeline.analyze(
        text=payload.text,
        skip_ai=payload.skip_ai
    )

    # Step 2: Compute confidence rating and summary breakdown
    confidence_score, confidence_rating, summary = confidence_router.compute_routing(issues)

    processing_time_ms = round((time.perf_counter() - t0) * 1000, 2)

    doc_id = payload.document_id

    # Step 3: If document_id is provided, persist analysis record in DB
    if doc_id:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        version_num = doc.current_version if doc else 1

        record = AnalysisRecord(
            document_id=doc_id,
            version_number=version_num,
            confidence_score=confidence_score,
            confidence_rating=confidence_rating,
            ai_used=ai_used,
            safe_scan_applied=safe_scan_applied,
            processing_time_ms=processing_time_ms,
            total_issues=summary["total_issues"],
            critical_issues=summary["critical"],
            warning_issues=summary["warning"],
            suggestion_issues=summary["suggestion"]
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Store individual issue records
        for iss in issues:
            issue_row = AnalysisIssue(
                analysis_id=record.id,
                document_id=doc_id,
                issue_type=iss["type"],
                severity=iss["severity"],
                matched_text=iss["matched_text"],
                start_offset=iss["start_offset"],
                end_offset=iss["end_offset"],
                reason=iss["reason"],
                suggested_fix=iss.get("suggested_fix"),
                source=iss.get("source"),
                source_id=iss.get("source_id"),
                confidence=iss.get("confidence", 1.0),
                intent_preserved=iss.get("intent_preserved", True)
            )
            db.add(issue_row)

        # Audit log entry
        audit = AuditLog(
            document_id=doc_id,
            user_id=current_user.id if current_user else None,
            user_email=current_user.email if current_user else "anonymous",
            action="analyzed",
            details_json=json.dumps({
                "confidence_score": confidence_score,
                "confidence_rating": confidence_rating,
                "total_issues": summary["total_issues"],
                "ai_used": ai_used
            })
        )
        db.add(audit)
        db.commit()

    return AnalyzeResponse(
        document_id=doc_id,
        status="completed",
        confidence_score=confidence_score,
        confidence_rating=confidence_rating,
        ai_used=ai_used,
        safe_scan_applied=safe_scan_applied,
        processing_time_ms=processing_time_ms,
        summary=SummaryOut(**summary),
        issues=[IssueOut(**iss) for iss in issues]
    )

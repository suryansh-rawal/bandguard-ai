import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document
from app.models.review import Comment
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.review import (
    SubmitReviewResponse, ApproveResponse, RequestChangesRequest,
    RequestChangesResponse, CommentCreate, CommentOut, AuditLogOut
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter(prefix="/documents", tags=["Review & Workflow"])

@router.post("/{document_id}/submit", response_model=SubmitReviewResponse)
def submit_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Submit document for approval (moves status to in_review)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    now = datetime.now(timezone.utc)
    doc.status = "in_review"
    doc.updated_at = now

    audit = AuditLog(
        document_id=doc.id,
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else "anonymous",
        action="submitted_for_review",
        details_json=json.dumps({"version": doc.current_version})
    )
    db.add(audit)
    db.commit()

    return SubmitReviewResponse(id=doc.id, status=doc.status, submitted_at=now)

@router.post("/{document_id}/approve", response_model=ApproveResponse)
def approve_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Approve document (moves status to approved)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    now = datetime.now(timezone.utc)
    doc.status = "approved"
    doc.updated_at = now

    approver_id = current_user.id if current_user else "reviewer_system"

    audit = AuditLog(
        document_id=doc.id,
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else "reviewer",
        action="approved",
        details_json=json.dumps({"version": doc.current_version, "approved_by": approver_id})
    )
    db.add(audit)
    db.commit()

    return ApproveResponse(id=doc.id, status=doc.status, approved_by=approver_id, approved_at=now)

@router.post("/{document_id}/request-changes", response_model=RequestChangesResponse)
def request_changes(
    document_id: str,
    payload: RequestChangesRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Request changes on document with feedback reason."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    now = datetime.now(timezone.utc)
    doc.status = "changes_requested"
    doc.updated_at = now

    audit = AuditLog(
        document_id=doc.id,
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else "reviewer",
        action="changes_requested",
        details_json=json.dumps({"reason": payload.reason, "version": doc.current_version})
    )
    db.add(audit)
    db.commit()

    return RequestChangesResponse(
        id=doc.id,
        status=doc.status,
        reason=payload.reason,
        reviewed_at=now
    )

@router.post("/{document_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    document_id: str,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Add a review comment to a document (optionally linked to text offset)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    author_name = current_user.full_name if current_user else "Reviewer"
    author_id = current_user.id if current_user else None

    comment = Comment(
        document_id=doc.id,
        author_id=author_id,
        author_name=author_name,
        content=comment_in.content,
        start_offset=comment_in.start_offset,
        end_offset=comment_in.end_offset
    )
    db.add(comment)

    audit = AuditLog(
        document_id=doc.id,
        user_id=author_id,
        user_email=current_user.email if current_user else "anonymous",
        action="comment_added",
        details_json=json.dumps({"comment_length": len(comment_in.content)})
    )
    db.add(audit)
    db.commit()
    db.refresh(comment)

    return comment

@router.get("/{document_id}/comments", response_model=List[CommentOut])
def get_comments(document_id: str, db: Session = Depends(get_db)):
    """List all comments on a document."""
    comments = db.query(Comment).filter(
        Comment.document_id == document_id
    ).order_by(Comment.created_at.asc()).all()
    return comments

@router.get("/{document_id}/audit-log", response_model=List[AuditLogOut])
def get_audit_log(document_id: str, db: Session = Depends(get_db)):
    """Retrieve complete audit history for a document."""
    logs = db.query(AuditLog).filter(
        AuditLog.document_id == document_id
    ).order_by(AuditLog.created_at.asc()).all()

    results = []
    for log in logs:
        try:
            details = json.loads(log.details_json) if log.details_json else {}
        except Exception:
            details = {}
        results.append(AuditLogOut(
            id=log.id,
            document_id=log.document_id,
            user_id=log.user_id,
            user_email=log.user_email,
            action=log.action,
            details=details,
            created_at=log.created_at
        ))
    return results

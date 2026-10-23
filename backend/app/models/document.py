import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False)
    status = Column(String(50), default="draft", index=True)  # draft, in_review, approved, changes_requested
    current_version = Column(Integer, default=1)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    creator = relationship("User", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan", order_by="desc(DocumentVersion.version_number)")
    comments = relationship("Comment", back_populates="document", cascade="all, delete-orphan")
    analysis_records = relationship("AnalysisRecord", back_populates="document", cascade="all, delete-orphan")

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String(36), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship
    document = relationship("Document", back_populates="versions")

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=True, index=True)
    version_number = Column(Integer, default=1)
    confidence_score = Column(Float, default=100.0)
    confidence_rating = Column(String(20), default="green")  # green, yellow, red
    ai_used = Column(Boolean, default=False)
    safe_scan_applied = Column(Boolean, default=False)
    processing_time_ms = Column(Float, default=0.0)
    total_issues = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    warning_issues = Column(Integer, default=0)
    suggestion_issues = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    document = relationship("Document", back_populates="analysis_records")
    issues = relationship("AnalysisIssue", back_populates="analysis_record", cascade="all, delete-orphan")

class AnalysisIssue(Base):
    __tablename__ = "analysis_issues"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    analysis_id = Column(String(36), ForeignKey("analysis_records.id"), nullable=False, index=True)
    document_id = Column(String(36), nullable=True, index=True)
    issue_type = Column(String(50), nullable=False)  # banned_term, preferred_term, unverified_claim, expired_fact, tone_mismatch
    severity = Column(String(20), nullable=False)    # critical, warning, suggestion
    matched_text = Column(Text, nullable=False)
    start_offset = Column(Integer, default=0)
    end_offset = Column(Integer, default=0)
    reason = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    source_id = Column(String(100), nullable=True)
    confidence = Column(Float, default=1.0)
    intent_preserved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    analysis_record = relationship("AnalysisRecord", back_populates="issues")

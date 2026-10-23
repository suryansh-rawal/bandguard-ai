import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.document import Document, DocumentVersion
from app.models.audit import AuditLog
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentOut, DocumentVersionOut, UploadResponse
from app.services.document_extractor import document_extractor
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    K12: Ingest and extract text from DOCX, PDF, or TXT files.
    Creates a new draft Document and initial DocumentVersion.
    """
    filename = file.filename or "uploaded_document.txt"
    doc_title = title or filename
    content_bytes = await file.read()

    try:
        extracted_text, file_type = document_extractor.extract_text(filename, content_bytes)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text extraction failed: {str(e)}"
        )

    # Create document
    new_doc = Document(
        title=doc_title,
        status="draft",
        current_version=1,
        created_by=current_user.id if current_user else None
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)

    # Create initial version
    version = DocumentVersion(
        document_id=new_doc.id,
        version_number=1,
        content=extracted_text,
        created_by=current_user.id if current_user else None
    )
    db.add(version)

    # Audit log
    audit = AuditLog(
        document_id=new_doc.id,
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else "anonymous",
        action="document_uploaded",
        details_json=json.dumps({"filename": filename, "file_type": file_type, "char_count": len(extracted_text)})
    )
    db.add(audit)
    db.commit()

    return UploadResponse(
        document_id=new_doc.id,
        title=new_doc.title,
        filename=filename,
        file_type=file_type,
        character_count=len(extracted_text),
        extracted_text=extracted_text
    )

@router.post("", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def create_document(
    doc_in: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new draft document."""
    doc = Document(
        title=doc_in.title,
        status="draft",
        current_version=1,
        created_by=current_user.id if current_user else None
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    version = DocumentVersion(
        document_id=doc.id,
        version_number=1,
        content=doc_in.content,
        created_by=current_user.id if current_user else None
    )
    db.add(version)

    audit = AuditLog(
        document_id=doc.id,
        user_id=current_user.id if current_user else None,
        user_email=current_user.email if current_user else "anonymous",
        action="document_created",
        details_json=json.dumps({"title": doc.title, "version": 1})
    )
    db.add(audit)
    db.commit()

    doc_out = DocumentOut.model_validate(doc)
    doc_out.content = doc_in.content
    return doc_out

@router.get("", response_model=List[DocumentOut])
def list_documents(
    doc_status: Optional[str] = Query(None, alias="status"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """List documents with optional status filtering."""
    query = db.query(Document)
    if doc_status:
        query = query.filter(Document.status == doc_status)
    docs = query.order_by(Document.updated_at.desc()).offset(skip).limit(limit).all()

    results = []
    for d in docs:
        out = DocumentOut.model_validate(d)
        latest_ver = db.query(DocumentVersion).filter(
            DocumentVersion.document_id == d.id,
            DocumentVersion.version_number == d.current_version
        ).first()
        out.content = latest_ver.content if latest_ver else ""
        results.append(out)

    return results

@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Retrieve document by ID with current version content."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    out = DocumentOut.model_validate(doc)
    latest_ver = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == doc.id,
        DocumentVersion.version_number == doc.current_version
    ).first()
    out.content = latest_ver.content if latest_ver else ""
    return out

@router.put("/{document_id}", response_model=DocumentOut)
def update_document(
    document_id: str,
    doc_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Update document content or title; increments version number."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc_update.title:
        doc.title = doc_update.title

    new_content = ""
    if doc_update.content is not None:
        doc.current_version += 1
        new_version = DocumentVersion(
            document_id=doc.id,
            version_number=doc.current_version,
            content=doc_update.content,
            created_by=current_user.id if current_user else None
        )
        db.add(new_version)
        new_content = doc_update.content

        audit = AuditLog(
            document_id=doc.id,
            user_id=current_user.id if current_user else None,
            user_email=current_user.email if current_user else "anonymous",
            action="document_updated",
            details_json=json.dumps({"version": doc.current_version})
        )
        db.add(audit)

    db.commit()
    db.refresh(doc)

    out = DocumentOut.model_validate(doc)
    out.content = new_content
    return out

@router.get("/{document_id}/versions", response_model=List[DocumentVersionOut])
def get_document_versions(document_id: str, db: Session = Depends(get_db)):
    """Retrieve all historical versions for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    versions = db.query(DocumentVersion).filter(
        DocumentVersion.document_id == document_id
    ).order_by(DocumentVersion.version_number.desc()).all()

    return versions

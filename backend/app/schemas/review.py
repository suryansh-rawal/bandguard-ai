from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SubmitReviewResponse(BaseModel):
    id: str
    status: str
    submitted_at: datetime

class ApproveResponse(BaseModel):
    id: str
    status: str
    approved_by: Optional[str] = None
    approved_at: datetime

class RequestChangesRequest(BaseModel):
    reason: str = Field(..., min_length=2)

class RequestChangesResponse(BaseModel):
    id: str
    status: str
    reason: str
    reviewed_at: datetime

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None

class CommentOut(BaseModel):
    id: str
    document_id: str
    author_id: Optional[str] = None
    author_name: str
    content: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    resolved: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogOut(BaseModel):
    id: str
    document_id: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    details: Dict[str, Any] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

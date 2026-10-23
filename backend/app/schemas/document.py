from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class DocumentVersionOut(BaseModel):
    id: str
    document_id: str
    version_number: int
    content: str
    created_by: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DocumentOut(BaseModel):
    id: str
    title: str
    status: str
    current_version: int
    content: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UploadResponse(BaseModel):
    document_id: str
    title: str
    filename: str
    file_type: str
    character_count: int
    extracted_text: str

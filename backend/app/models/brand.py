import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(String(50), primary_key=True)  # e.g., TONE-01
    brand_name = Column(String(100), default="BrandGuard AI")
    code = Column(String(50), index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), default="tone")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class GlossaryRule(Base):
    __tablename__ = "glossary_rules"

    id = Column(String(50), primary_key=True)  # e.g., BAN-001, PREF-001
    rule_type = Column(String(20), index=True, nullable=False)  # 'banned' or 'preferred'
    term = Column(String(255), nullable=False)
    patterns_json = Column(Text, default="[]")  # List of regex strings in JSON
    preferred = Column(String(255), nullable=True)  # For preferred terms
    alternatives_json = Column(Text, default="[]")  # For banned terms
    reason = Column(Text, nullable=False)
    severity = Column(String(20), default="warning")  # critical, warning, suggestion
    source = Column(String(100), default="Brand Kit - Glossary v1.2")
    category = Column(String(50), default="general")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FactVaultItem(Base):
    __tablename__ = "fact_vault_items"

    id = Column(String(50), primary_key=True)  # e.g., FV-001
    statement = Column(Text, nullable=False)
    source = Column(String(255), nullable=False)
    category = Column(String(50), default="General")
    keywords_json = Column(Text, default="[]")
    verified_date = Column(String(20), nullable=True)
    expires_on = Column(String(20), nullable=False)  # ISO Date YYYY-MM-DD
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

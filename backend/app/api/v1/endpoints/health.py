from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.config import settings
from app.services.rules_engine import rules_engine
from app.services.fact_vault import fact_vault

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive service health and subsystem readiness check."""
    # Check DB
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check AI status
    if settings.ANTHROPIC_API_KEY:
        ai_status = f"ready (Claude 3.5: {settings.CLAUDE_MODEL})"
    elif settings.GEMINI_API_KEY:
        ai_status = f"ready (Google Gemini: {settings.GEMINI_MODEL})"
    else:
        ai_status = "fallback_mode (rules & heuristic)"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ai_status": ai_status,
        "brand_kit_loaded": len(rules_engine.banned_rules) > 0,
        "facts_count": len(fact_vault.facts),
        "banned_rules_count": len(rules_engine.banned_rules),
        "preferred_rules_count": len(rules_engine.preferred_rules),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

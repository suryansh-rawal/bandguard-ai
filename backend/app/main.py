import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, SessionLocal, Base
from app.core.security import hash_password
from app.models.user import User
from app.models.brand import BrandGuideline, GlossaryRule, FactVaultItem
from app.api.v1.router import api_router
from app.services.rules_engine import rules_engine
from app.services.fact_vault import fact_vault
from app.services.citation_validator import citation_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrandGuard.Main")

def seed_database():
    """Seed database with Brand Kit rules, facts, and initial demo users if not present."""
    db = SessionLocal()
    try:
        # 1. Seed demo users
        if db.query(User).count() == 0:
            logger.info("Seeding initial demo users...")
            demo_users = [
                User(
                    email="creator@brandguard.ai",
                    hashed_password=hash_password("Creator123!"),
                    full_name="Alex Creator",
                    role="creator"
                ),
                User(
                    email="reviewer@brandguard.ai",
                    hashed_password=hash_password("Reviewer123!"),
                    full_name="Morgan Reviewer",
                    role="reviewer"
                ),
                User(
                    email="manager@brandguard.ai",
                    hashed_password=hash_password("Manager123!"),
                    full_name="Taylor Manager",
                    role="manager"
                )
            ]
            db.add_all(demo_users)
            db.commit()

        # 2. Seed brand kit data if brand_kit.json exists
        kit_path = settings.BRAND_KIT_PATH
        if kit_path.exists() and db.query(FactVaultItem).count() == 0:
            logger.info(f"Loading {kit_path.name} into database...")
            with open(kit_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Seed guidelines
            for g in data.get("brand", {}).get("tone_principles", []):
                guideline = BrandGuideline(
                    id=g["id"],
                    brand_name=data.get("brand", {}).get("name", "BrandGuard AI"),
                    code=g["id"],
                    title=g["name"],
                    description=g["description"],
                    category="tone"
                )
                db.merge(guideline)

            # Seed glossary rules
            glossary = data.get("glossary", {})
            for b in glossary.get("banned_terms", []):
                rule = GlossaryRule(
                    id=b["id"],
                    rule_type="banned",
                    term=b["term"],
                    patterns_json=json.dumps(b.get("patterns", [])),
                    alternatives_json=json.dumps(b.get("alternatives", [])),
                    reason=b.get("reason", ""),
                    severity=b.get("severity", "critical"),
                    source=b.get("source", "Brand Kit - Glossary v1.2"),
                    category=b.get("category", "compliance")
                )
                db.merge(rule)

            for p in glossary.get("preferred_terms", []):
                rule = GlossaryRule(
                    id=p["id"],
                    rule_type="preferred",
                    term=p["term"],
                    patterns_json=json.dumps(p.get("patterns", [])),
                    preferred=p.get("preferred", ""),
                    reason=p.get("reason", ""),
                    severity=p.get("severity", "suggestion"),
                    source=p.get("source", "Brand Kit - Glossary v1.2"),
                    category="style"
                )
                db.merge(rule)

            # Seed Fact Vault items
            for fv in data.get("fact_vault", []):
                item = FactVaultItem(
                    id=fv["id"],
                    statement=fv["statement"],
                    source=fv["source"],
                    category=fv.get("category", "General"),
                    keywords_json=json.dumps(fv.get("keywords", [])),
                    verified_date=fv.get("verified_date"),
                    expires_on=fv.get("expires_on")
                )
                db.merge(item)

            db.commit()
            logger.info("Database successfully seeded with Brand Kit and Fact Vault items.")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

# Initialize tables, seed brand kit and load rules synchronously on startup
Base.metadata.create_all(bind=engine)
seed_database()
rules_engine.load_rules()
fact_vault.load_facts()
citation_validator.load_valid_sources()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Brand Safety, Claim Verification, and Tone Governance API.",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "service": "BrandGuard AI Backend",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

@app.get("/health")
def root_health():
    """Direct alias for /health without v1 prefix."""
    from app.api.v1.endpoints.health import health_check
    db = SessionLocal()
    try:
        return health_check(db=db)
    finally:
        db.close()

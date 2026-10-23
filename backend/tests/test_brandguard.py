import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.services.rules_engine import rules_engine
from app.services.safe_scan import safe_scan
from app.services.fact_vault import fact_vault
from app.services.claim_passport import ClaimPassport
from app.services.citation_validator import citation_validator
from app.services.intent_lock import intent_lock
from app.services.confidence_router import confidence_router

client = TestClient(app)

# ==============================================================================
# Unit Tests: Rules Engine (K3)
# ==============================================================================
def test_rules_engine_banned_terms():
    text = "We promise guaranteed 100% uptime and our system is unhackable."
    issues = rules_engine.scan(text)
    
    assert len(issues) >= 2
    banned_types = [i["type"] for i in issues]
    assert all(t == "banned_term" for t in banned_types)
    
    matched = [i["matched_text"].lower() for i in issues]
    assert any("guaranteed 100% uptime" in m for m in matched)
    assert any("unhackable" in m for m in matched)

def test_rules_engine_preferred_terms():
    text = "Please log on to the Brandguard work space for AI powered workflows."
    issues = rules_engine.scan(text)
    
    types = [i["type"] for i in issues]
    assert "preferred_term" in types
    
    fixes = {i["matched_text"]: i["suggested_fix"] for i in issues if i["type"] == "preferred_term"}
    assert "Brandguard" in fixes and fixes["Brandguard"] == "BrandGuard"
    assert "AI powered" in fixes and fixes["AI powered"] == "AI-powered"

# ==============================================================================
# Unit Tests: Safe Scan PII Masking (K8)
# ==============================================================================
def test_safe_scan_pii_masking():
    raw_text = "For inquiries, email support@example.com or reach out to John Doe at +1-555-0199."
    result = safe_scan.mask(raw_text)
    
    assert result.applied is True
    assert "support@example.com" not in result.masked_text
    assert "[EMAIL_REDACTED_1]" in result.masked_text
    assert "[PHONE_REDACTED_" in result.masked_text
    
    # Test bidirectional unmasking
    unmasked = safe_scan.unmask(result.masked_text, result.replacements)
    assert "support@example.com" in unmasked
    assert "+1-555-0199" in unmasked

# ==============================================================================
# Unit Tests: Fact Vault & Claim Passport (K4 & Round 3 Improvement)
# ==============================================================================
def test_claim_passport_expired_fact():
    # Set reference date to October 2026, where FV-003 expired on 2026-06-30
    passport = ClaimPassport(reference_date=date(2026, 10, 23))
    text = "We currently have over 10,000 active enterprise teams globally across our platforms."
    issues = passport.evaluate_claims(text)
    
    assert len(issues) >= 1
    expired = [i for i in issues if i["type"] == "expired_fact"]
    assert len(expired) >= 1
    assert "FV-003" in expired[0]["source_id"]
    assert "2026-06-30" in expired[0]["reason"]

def test_claim_passport_valid_fact():
    passport = ClaimPassport(reference_date=date(2026, 10, 23))
    # FV-001 expires on 2027-12-31, so it is valid
    text = "ApexCloud guarantees a 99.95% monthly uptime SLA backed by credits."
    issues = passport.evaluate_claims(text)
    # Should not be flagged as expired
    expired = [i for i in issues if i["type"] == "expired_fact"]
    assert len(expired) == 0

# ==============================================================================
# Unit Tests: Citation Validator (K6)
# ==============================================================================
def test_citation_validator_valid_and_hallucinated():
    # Genuine source
    assert citation_validator.is_valid_source("Brand Kit - Glossary v1.2", "BAN-001") is True
    assert citation_validator.is_valid_source("Security & Trust Portal 2026", "FV-002") is True
    
    # Hallucinated source
    assert citation_validator.is_valid_source("Random Internet Policy 2024", "FAKE-999") is False
    
    # Filter list
    sample_issues = [
        {"matched_text": "sample1", "source": "Master Service Agreement v4.1", "source_id": "FV-001"},
        {"matched_text": "sample2", "source": "Invented Guidelines 404", "source_id": "G-999"}
    ]
    valid, rejected = citation_validator.validate_issues(sample_issues)
    assert len(valid) == 1
    assert len(rejected) == 1
    assert valid[0]["source_id"] == "FV-001"
    assert rejected[0]["source_id"] == "G-999"

# ==============================================================================
# Unit Tests: Intent Lock (K7)
# ==============================================================================
def test_intent_lock():
    # Intent preserved (uptime SLA replacement)
    preserved, _, _ = intent_lock.verify_fix("guaranteed 100% uptime", "99.95% monthly uptime SLA backed by credits")
    assert preserved is True

    # Polarity flip (secure -> not secure)
    flipped, _, reason = intent_lock.verify_fix("our software is secure", "our software is not secure")
    assert flipped is False
    assert "negation" in reason.lower()

# ==============================================================================
# Unit Tests: Confidence Router (K9)
# ==============================================================================
def test_confidence_router():
    # Clean text -> Green
    score_green, rating_green, _ = confidence_router.compute_routing([])
    assert score_green == 100.0
    assert rating_green == "green"

    # Critical issue -> Red
    score_red, rating_red, summary = confidence_router.compute_routing([
        {"severity": "critical", "type": "banned_term"}
    ])
    assert score_red <= 75.0
    assert rating_red == "red"
    assert summary["critical"] == 1

# ==============================================================================
# Integration Tests: Endpoints (K1, K2, K10, K11, K12, K13)
# ==============================================================================
def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["brand_kit_loaded"] is True
    assert data["facts_count"] > 0

def test_auth_and_protected_flow():
    import time
    test_email = f"reviewer.{int(time.time()*1000)}@brandguard.ai"
    # Register new user
    reg_res = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "Password123!",
        "full_name": "Test Reviewer",
        "role": "reviewer"
    })
    assert reg_res.status_code == 201
    
    # Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    
    # Get Profile with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == test_email

def test_analyze_endpoint_real_results():
    payload = {
        "text": "Welcome to Brandguard! We provide guaranteed 100% uptime with over 10,000 active enterprise teams globally.",
        "skip_ai": True  # Tests deterministic fallback & rules engine directly
    }
    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert data["ai_used"] is False
    assert len(data["issues"]) >= 2
    
    issue_types = [i["type"] for i in data["issues"]]
    assert "banned_term" in issue_types
    assert "preferred_term" in issue_types

def test_document_lifecycle_and_review_workflow():
    # 1. Create document
    create_res = client.post("/api/v1/documents", json={
        "title": "Q4 Press Release",
        "content": "Our system offers revolutionary magic and guaranteed 100% uptime."
    })
    assert create_res.status_code == 201
    doc = create_res.json()
    doc_id = doc["id"]
    assert doc["status"] == "draft"

    # 2. Analyze document
    analyze_res = client.post("/api/v1/analyze", json={
        "text": doc["content"],
        "document_id": doc_id,
        "skip_ai": True
    })
    assert analyze_res.status_code == 200
    assert analyze_res.json()["summary"]["critical"] >= 1

    # 3. Submit for review
    submit_res = client.post(f"/api/v1/documents/{doc_id}/submit")
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "in_review"

    # 4. Add review comment
    comment_res = client.post(f"/api/v1/documents/{doc_id}/comments", json={
        "content": "Please replace the 100% uptime claim with our 99.95% SLA.",
        "start_offset": 40,
        "end_offset": 62
    })
    assert comment_res.status_code == 201
    assert comment_res.json()["document_id"] == doc_id

    # 5. Request changes
    change_res = client.post(f"/api/v1/documents/{doc_id}/request-changes", json={
        "reason": "Address SLA and magic hype before publication."
    })
    assert change_res.status_code == 200
    assert change_res.json()["status"] == "changes_requested"

    # 6. Update document with fix (increments version)
    update_res = client.put(f"/api/v1/documents/{doc_id}", json={
        "content": "Our system offers cutting-edge architecture and 99.95% monthly uptime SLA backed by credits."
    })
    assert update_res.status_code == 200
    assert update_res.json()["current_version"] == 2

    # 7. Resubmit & Approve
    client.post(f"/api/v1/documents/{doc_id}/submit")
    approve_res = client.post(f"/api/v1/documents/{doc_id}/approve")
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"

    # 8. Check audit log
    audit_res = client.get(f"/api/v1/documents/{doc_id}/audit-log")
    assert audit_res.status_code == 200
    actions = [a["action"] for a in audit_res.json()]
    assert "document_created" in actions
    assert "analyzed" in actions
    assert "submitted_for_review" in actions
    assert "comment_added" in actions
    assert "changes_requested" in actions
    assert "approved" in actions

def test_document_upload_text_file():
    file_content = b"ApexCloud delivers enterprise AI safety with on-premises deployment."
    files = {"file": ("draft.txt", file_content, "text/plain")}
    res = client.post("/api/v1/documents/upload", files=files, data={"title": "Uploaded Draft"})
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Uploaded Draft"
    assert data["file_type"] == "txt"
    assert "enterprise AI safety" in data["extracted_text"]

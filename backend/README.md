# BrandGuard AI — Backend Service
**Team Tech Titans** · **Round 2 Deliverable** · **Backend Lead: Kanishka**

BrandGuard AI is an enterprise guardrail engine that audits marketing, technical, and sales drafts against brand tone, banned vocabulary, regulatory compliance, and factual validity.

---

## Features Implemented

- **K1: FastAPI Architecture:** Async REST API with modular structure, Pydantic V2 schemas, and zero-overhead performance.
- **API Contract (`API_CONTRACT.md`):** Complete frozen specifications for `/analyze`, documents, review workflow, and health check.
- **K2: Relational Database Schema:** SQLAlchemy models supporting PostgreSQL and SQLite. Tracks users, guidelines, facts, documents, versions, issues, comments, and audit logs.
- **K3: Deterministic Rules Engine:** High-speed regex scanner with morphological inflection and word boundary matching for banned and preferred glossary terms.
- **K4: Claim Extraction & Fact Vault Retrieval:** Parses quantitative claims and matches against verified Fact Vault entries.
- **K5: Claude 3.5 Sonnet Integration:** Structured AI analysis returning type-safe JSON findings.
- **K6: Citation Validation (Anti-Hallucination):** Strictly rejects any finding whose source does not exist in authorized Brand Kit records.
- **K7: Intent Lock:** Verifies suggested fixes preserve communicative intent and prevents unintended polarity negation.
- **K8: Safe Scan:** Anonymizes PII (phones, emails, personal names) before AI egress, with lossless offset remapping.
- **K9: Confidence Routing:** Calculates composite compliance score (0-100) and routes content into **Green**, **Yellow**, or **Red** workflows.
- **K10: Review & Approval Workflow:** Full document lifecycle (`draft` -> `in_review` -> `approved` / `changes_requested`), inline commenting, version history, and audit trail.
- **K11: Role-Based Authentication:** JWT Bearer authentication with roles: `creator`, `manager`, `reviewer`.
- **K12: File Ingestion:** Automated text extraction for `.docx`, `.pdf`, and `.txt` uploads.
- **K13: Zero-Downtime Fallback:** If AI is unavailable or fails, returns complete rule & Fact Vault findings with `ai_used: false`. Never fails with 500.
- **Round 3 Improvement (Claim Passport):** Flags claims whose Fact Vault validity `expires_on` has elapsed.
- **K14: Cloud Deployment Ready:** Includes `Dockerfile`, `Procfile`, and `render.yaml` for Render and Railway deployments.

---

## Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py         # Login, register, profile
│   │       │   ├── analyze.py      # Core /analyze endpoint
│   │       │   ├── documents.py    # Drafts, versions, upload
│   │       │   ├── reviews.py      # Review, approve, comments, audit
│   │       │   └── health.py       # Health diagnostic endpoint
│   │       └── router.py
│   ├── core/
│   │   ├── config.py               # Environment configuration
│   │   ├── database.py             # SQLAlchemy engine & session
│   │   └── security.py             # Bcrypt hashing & JWT
│   ├── data/
│   │   └── brand_kit.json          # Brand guidelines & Fact Vault
│   ├── models/                     # SQLAlchemy DB entities
│   ├── schemas/                    # Pydantic request/response models
│   ├── services/
│   │   ├── rules_engine.py         # Banned & preferred terms
│   │   ├── safe_scan.py            # PII masking
│   │   ├── claim_extractor.py      # Assertive claim parsing
│   │   ├── fact_vault.py           # Approved facts matcher
│   │   ├── claim_passport.py       # Expiration check engine
│   │   ├── citation_validator.py   # Anti-hallucination verification
│   │   ├── intent_lock.py          # Semantic preservation guard
│   │   ├── confidence_router.py    # Score & Green/Yellow/Red routing
│   │   ├── ai_pipeline.py          # Claude API & fallback orchestrator
│   │   └── document_extractor.py   # PDF, DOCX, TXT parser
│   └── main.py                     # FastAPI application entrypoint
├── tests/
│   └── test_brandguard.py          # 13 comprehensive test suites
├── API_CONTRACT.md                 # Frozen API contract
├── ARCHITECTURE_AND_AI_PIPELINE.md # PDF documentation section
├── DAILY_SYNC.md                   # Daily standup notes
├── CHANGES_AND_BUGS.md             # Change management tracking
├── Dockerfile                      # Container definition
├── Procfile                        # Heroku/Railway process file
├── render.yaml                     # Render blueprint configuration
├── requirements.txt                # Python dependencies
└── README.md
```

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (e.g. `uv` or `venv`)

### 2. Installation
```bash
# Clone and enter backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Key configuration items:
- `DATABASE_URL`: `sqlite:///./brandguard.db` (or PostgreSQL connection URI)
- `ANTHROPIC_API_KEY`: Your Claude API key (optional; if omitted, deterministic fallback activates automatically)

### 4. Running the Server
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://localhost:8000/docs`
- Redoc Alternative Docs: `http://localhost:8000/redoc`
- Health Diagnostic: `http://localhost:8000/api/v1/health`

---

## Running Automated Tests

Run the full test suite with `pytest`:
```bash
pytest -v
```
All 13 test suites validate rules matching, PII safe scan, Claim Passport, citation checking, intent lock, and review lifecycle.

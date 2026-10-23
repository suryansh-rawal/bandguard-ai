# Daily Sync Notes — Team Tech Titans
**Facilitator:** Kanishka (Backend Lead) · **Participant:** Suryansh (Frontend Lead)  
**Sprint:** Round 2 (22 Oct - 25 Oct 2026)

---

## Day 1: 22 Oct 2026 (Foundation)
- **Done:**
  - Initialized FastAPI backend skeleton inside `/backend`.
  - Authored and froze `API_CONTRACT.md` covering all endpoints, response schemas, and error shapes.
  - Implemented complete SQLAlchemy schema: `users`, `brand_guidelines`, `glossary_rules`, `fact_vault_items`, `documents`, `document_versions`, `analysis_records`, `analysis_issues`, `comments`, `audit_logs`.
  - Built auto-seeding engine that ingests `brand_kit.json` into memory and database at startup.
  - Implemented deterministic Rules Engine (`rules_engine.py`) covering banned and preferred terms with inflection and word boundaries.
  - Verified `/analyze` returns real rule-based issues in contract format with sub-10ms response time.
- **Doing:**
  - Integrating Safe Scan and Claim Extraction for Day 2 pipeline.
- **Blocked:**
  - None.

---

## Day 2: 23 Oct 2026 (AI and Evidence)
- **Done:**
  - Built Claim Extraction (`claim_extractor.py`) to parse numerical metrics, SLAs, and compliance claims.
  - Implemented Fact Vault retrieval (`fact_vault.py`) with token overlap, keyword matching, and number validation.
  - Integrated Round 3 improvement: **Claim Passport** (`claim_passport.py`) flagging expired facts with `expires_on < today`.
  - Integrated Anthropic Claude 3.5 Sonnet API (`ai_pipeline.py`) with structured system prompts and JSON schema output.
  - Built Citation Validation (`citation_validator.py`) strictly enforcing that hallucinated guidelines or sources are rejected.
  - Implemented Intent Lock (`intent_lock.py`) ensuring AI suggested fixes maintain communicative polarity and domain topic.
  - Implemented Safe Scan (`safe_scan.py`) masking PII (phones, emails, names) before LLM egress.
  - Hosted integration sync with Suryansh; validated frontend against live backend endpoints.
- **Doing:**
  - Finalizing review endpoints, confidence routing, and deployment configurations.
- **Blocked:**
  - None.

---

## Day 3: 24 Oct 2026 (Workflow and Deployment)
- **Done:**
  - Implemented Confidence Router (`confidence_router.py`) computing weighted penalty scores and Green/Yellow/Red status.
  - Implemented AI Fallback Guarantee (`ai_pipeline.py`): on AI timeout or failure, seamlessly returns rule & Fact Vault findings with `ai_used: false`.
  - Implemented Review & Approval lifecycle endpoints: `/submit`, `/approve`, `/request-changes`, `/comments`, `/versions`, `/audit-log`.
  - Implemented JWT authentication and role-based access control (`creator`, `manager`, `reviewer`).
  - Implemented multi-format document text extraction (`document_extractor.py`) supporting `.docx`, `.pdf`, `.txt`.
  - Prepared containerization & deployment configs: `Dockerfile`, `Procfile`, `render.yaml`, `.env.example`.
  - Authored comprehensive documentation: `ARCHITECTURE_AND_AI_PIPELINE.md` for PDF submission.
  - Ran automated test suite with 100% test pass rate across all 13 test modules.
- **Doing:**
  - Feature freeze in the evening. Ready for live staging verification.
- **Blocked:**
  - None.

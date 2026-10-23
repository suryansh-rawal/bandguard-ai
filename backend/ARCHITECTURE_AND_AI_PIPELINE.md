# BrandGuard AI — Backend Architecture & AI Pipeline Documentation
**Project:** BrandGuard AI (Team Tech Titans) · **Author:** Kanishka (Backend Lead)  
**Deliverable for Round 2 Submission (PDF Sections)**

---

## 1. System Architecture

BrandGuard AI is engineered as a modular, high-throughput backend service designed to ensure brand safety, factual integrity, and regulatory compliance across marketing, legal, and engineering communications.

```
+-----------------------------------------------------------------------------------+
|                                Client Applications                                 |
|             (React Web UI / Suryansh Frontend / Chrome Extension / API)           |
+-----------------------------------------------------------------------------------+
                                          |
                                          | HTTPS / REST (JWT Bearer Auth)
                                          v
+-----------------------------------------------------------------------------------+
|                             FastAPI Application Layer                             |
|  - CORS Middleware & Security      - /api/v1/auth (JWT, Roles: Creator/Reviewer)  |
|  - Lifespan DB & Seed Management   - /api/v1/documents (Drafts, Versions, Upload)  |
|  - /api/v1/analyze Orchestrator    - /api/v1/reviews (Submit, Approve, Comments)  |
+-----------------------------------------------------------------------------------+
       |                                      |                               |
       v                                      v                               v
+-----------------------+   +------------------------------+   +--------------------+
|  Deterministic Engine |   |   Evidence & Claims Layer    |   | Safe AI Pipeline   |
|-----------------------|   |------------------------------|   |--------------------|
| - Rules Engine        |   | - Claim Extractor            |   | - Safe Scan (PII)  |
|   (Banned/Preferred)  |   | - Fact Vault Matcher         |   | - Claude 3.5 Sonnet|
| - Word boundary regex |   | - Claim Passport             |   | - Citation Validate|
| - Character offsets   |   |   (Temporal Expiration Check)|   | - Intent Lock Fix  |
+-----------------------+   +------------------------------+   +--------------------+
       \                                      |                               /
        \                                     v                              /
         +------------------------------------------------------------------+
         |               K9: Confidence Router & Scoring                    |
         |  - Deductions: Critical (-25), Warning (-12), Suggestion (-3)    |
         |  - Output: Score (0-100) & Route: Green / Yellow / Red           |
         +------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                                 Persistence Layer                                 |
|  - PostgreSQL (Production / Railway / Render) & SQLite (Zero-Config Development)  |
|  - Tables: users, brand_guidelines, glossary_rules, fact_vault_items, documents,  |
|    document_versions, analysis_records, analysis_issues, comments, audit_logs     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Multi-Stage AI Pipeline & Guaranteed Fallback (K5, K8, K6, K7, K13)

### Pipeline Flowchart

```
[ Incoming Draft Text ]
           |
           +------------------------------------------+
           |                                          |
           v                                          v
[ K3: Rules Engine ]                       [ K4: Claim Extractor ]
(Banned & Preferred Glossary Scan)                    |
           |                                          v
           |                               [ K4: Fact Vault Search ]
           |                                          |
           |                                          v
           |                               [ Round 3: Claim Passport ]
           |                               (Check Fact `expires_on < today`)
           |                                          |
           +--------------------+---------------------+
                                |
                                v
               [ Are AI & Claude API Available? ]
                         /             \
                       NO               YES
                      /                   \
                     v                     v
          [ K13: AI Fallback ]      [ K8: Safe Scan PII Masking ]
          (Deterministic Issues)     (Mask Phones, Emails, Names)
                     |                     |
                     |                     v
                     |              [ Claude 3.5 Sonnet API ]
                     |              (Structured JSON Analysis)
                     |                     |
                     |                     v
                     |              [ K6: Citation Validation ]
                     |              (Reject Hallucinated Sources)
                     |                     |
                     |                     v
                     |              [ K7: Intent Lock Verification ]
                     |              (Ensure Fix Preserves Meaning)
                     |                     |
                     +---------------------+
                                |
                                v
                [ Merge & Deduplicate Spans ]
                                |
                                v
                [ K9: Confidence Router Scoring ]
                    (Green / Yellow / Red)
                                |
                                v
                    [ Final API Response ]
```

### Stage Details:
1. **K8: Safe Scan Pre-Processing:**
   Before any text is transmitted to third-party LLMs, Safe Scan anonymizes personally identifiable information (PII). Emails, international phone numbers, and employee/executive names are replaced with deterministic tokens (`[EMAIL_REDACTED_1]`, `[PHONE_REDACTED_1]`). A bidirectional offset restoration map is preserved so findings are accurately translated back to the author's original document positions.
2. **K5: Claude 3.5 Sonnet Structured Synthesis:**
   Draft copy is analyzed against active brand guidelines (TONE-01, TONE-02, TONE-03). The system prompt enforces a zero-markdown JSON array output schema providing `matched_text`, `type`, `severity`, `reason`, `source`, `source_id`, `suggested_fix`, and `confidence`.
3. **K6: Citation Validation (Anti-Hallucination Shield):**
   *Requirement Rule:* Any finding whose cited source does not resolve to an actual guideline, glossary entry, or Fact Vault record is rejected. Claude cannot hallucinate non-existent compliance policies.
4. **K7: Intent Lock Semantic Guard:**
   Validates whether a suggested revision preserves the author's core communicative intent. Checks polarity negation flips (e.g. flipping "secure" to "not secure") and verifies topic anchor terms so the suggested fix solves brand issues without altering intended technical meaning.
5. **K13: Guaranteed AI-Failure Fallback:**
   If the Anthropic API experiences network latency, timeouts, quota exhaustion, or malformed outputs, the pipeline catches the exception and returns the deterministic rules engine and Fact Vault heuristic findings with `ai_used: false`. The frontend will **never** receive a 500 error or blank screen.

---

## 3. Implementation Details

- **FastAPI Core (`/backend/app`):** Async request pipeline with type-safe Pydantic V2 models and sub-5ms routing overhead.
- **Rules Engine (`rules_engine.py`):** Pre-compiled regex tokenizers with word boundaries and morphological inflection matching (`\bguarantee(?:d|s|ing)? 100% uptime\b`).
- **Database Schema:** Full entity-relationship schema implemented in SQLAlchemy supporting PostgreSQL and SQLite. Automatically runs migrations and seeds `brand_kit.json` guidelines, glossary items, and fact vault records upon boot.
- **Workflow & Audit Log:** Complete review cycle tracking:
  - Document status: `draft` -> `in_review` -> `approved` or `changes_requested`.
  - Version incrementing on updates.
  - Granular immutable audit log entries recording timestamp, user email, action, and payload summary.
- **File Ingestion (`document_extractor.py`):** Direct binary stream extraction for `.docx`, `.pdf`, and `.txt` files.

---

## 4. Round 3 Improvement: Advanced Claim Verification (Claim Passport)

### What:
The **Claim Passport** is an enterprise temporal verification system that links every factual claim in marketing and sales drafts to a cryptographically tracked, time-stamped fact vault record equipped with an `expires_on` expiration lifecycle.

### Why:
Fast-growing enterprises frequently update critical metrics (e.g., quarterly customer counts, annual uptime percentages, compliance audit certificates). When marketing drafts use outdated metrics—such as citing *"over 10,000 customers"* from Q1 when the audit expired in June—the company incurs severe legal liability and customer distrust. Standard semantic matchers only check if the fact sounds familiar, completely ignoring whether the evidence is temporally obsolete.

### How:
1. **Claim Extraction:** The system uses syntactic regex and metric anchors to parse quantitative assertions (percentages, SLAs, customer metrics, certifications).
2. **Fact Vault Retrieval:** Claims are evaluated against Fact Vault records via multi-attribute keyword, number-match, and token-overlap scoring.
3. **Temporal Validity Check:** When a claim matches an authorized Fact Vault item (e.g. `FV-003: Over 10,000 active enterprise teams globally`), the Claim Passport evaluates its `expires_on` timestamp against the current date (`2026-10-23`). If `expires_on < current_date`, an `expired_fact` warning issue is automatically generated:
   > *"Claim references 'Over 10,000 active enterprise teams globally' (Fact Vault FV-003), but its verification expired on 2026-06-30 (Claim Passport warning)."*
4. **Resolution:** The system prompts the creator to update the metric to the latest audited version or triggers an internal request to marketing ops to renew the Fact Vault passport.

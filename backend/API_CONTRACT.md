# BrandGuard AI — Backend API Contract v1.0.0
**Team:** Tech Titans · **Author:** Kanishka (Backend Lead) · **Collaborator:** Suryansh (Frontend Lead)
**Status:** Frozen (Day 1 - 22 Oct) · **Base URL:** `/api/v1`

---

## 1. Overview & General Standards

- All requests and responses use `application/json` unless specified otherwise (e.g., file upload uses `multipart/form-data`).
- Standard HTTP status codes:
  - `200 OK`: Request succeeded.
  - `201 Created`: Resource created.
  - `400 Bad Request`: Validation failure or malformed payload.
  - `401 Unauthorized`: Missing or invalid Bearer JWT token.
  - `403 Forbidden`: Insufficient role permissions.
  - `404 Not Found`: Resource does not exist.
  - `422 Unprocessable Entity`: Schema validation error.
  - `500 Internal Server Error`: Server error (guaranteed fallback handles AI failures gracefully).
- Timestamps are formatted in ISO 8601 (`YYYY-MM-DDTHH:MM:SS.sssZ`).

---

## 2. Authentication & Authorization

All protected endpoints require the header:
```http
Authorization: Bearer <jwt_access_token>
```

### Roles:
- `creator`: Can upload, create, edit drafts, submit for review.
- `manager`: Can submit, approve, request changes, edit, view audit logs.
- `reviewer`: Can inspect documents, request changes, approve, and add comments.

---

### `POST /api/v1/auth/register`
Create a new user account.

**Request:**
```json
{
  "email": "creator@brandguard.ai",
  "password": "SecurePassword123!",
  "full_name": "Suryansh Creator",
  "role": "creator"
}
```

**Response (`201 Created`):**
```json
{
  "id": "usr_9f81a7b0-88df-41a2-b91c-1901a5e12f01",
  "email": "creator@brandguard.ai",
  "full_name": "Suryansh Creator",
  "role": "creator",
  "created_at": "2026-10-23T10:00:00.000Z"
}
```

---

### `POST /api/v1/auth/login`
Authenticate and obtain a JWT access token.

**Request:**
```json
{
  "email": "creator@brandguard.ai",
  "password": "SecurePassword123!"
}
```

**Response (`200 OK`):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "usr_9f81a7b0-88df-41a2-b91c-1901a5e12f01",
    "email": "creator@brandguard.ai",
    "full_name": "Suryansh Creator",
    "role": "creator"
  }
}
```

---

### `GET /api/v1/auth/me`
Retrieve the authenticated user's profile.

**Response (`200 OK`):**
```json
{
  "id": "usr_9f81a7b0-88df-41a2-b91c-1901a5e12f01",
  "email": "creator@brandguard.ai",
  "full_name": "Suryansh Creator",
  "role": "creator"
}
```

---

## 3. Brand Analysis (`/analyze`)

### `POST /api/v1/analyze`
Core endpoint analyzing text drafts for brand violations, banned terms, unverified claims, tone inconsistencies, and expired facts.

**Request:**
```json
{
  "text": "Welcome to Brandguard. We offer guaranteed 100% uptime with over 10,000 active enterprise teams globally! Contact john.doe@acme.com at +1-555-0199.",
  "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "skip_ai": false,
  "brand_id": "default"
}
```

**Response (`200 OK`):**
```json
{
  "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "completed",
  "confidence_score": 64.0,
  "confidence_rating": "yellow",
  "ai_used": true,
  "safe_scan_applied": true,
  "processing_time_ms": 138.4,
  "summary": {
    "total_issues": 3,
    "critical": 1,
    "warning": 1,
    "suggestion": 1
  },
  "issues": [
    {
      "id": "iss_a1b2c3d4-0001",
      "type": "banned_term",
      "severity": "critical",
      "matched_text": "guaranteed 100% uptime",
      "start_offset": 32,
      "end_offset": 54,
      "reason": "Absolute uptime guarantee violates SLA compliance policy.",
      "suggested_fix": "99.95% monthly uptime SLA backed by credits",
      "source": "Brand Kit - Glossary v1.2",
      "source_id": "glossary-term-001",
      "confidence": 1.0,
      "intent_preserved": true
    },
    {
      "id": "iss_a1b2c3d4-0002",
      "type": "expired_fact",
      "severity": "warning",
      "matched_text": "over 10,000 active enterprise teams globally",
      "start_offset": 60,
      "end_offset": 104,
      "reason": "Claim matches Fact Vault (FV-003) but the validity expired on 2026-06-30 (Claim Passport warning).",
      "suggested_fix": "Over 12,500 active enterprise teams globally (Q3 2026 update)",
      "source": "Fact Vault: FV-003",
      "source_id": "FV-003",
      "confidence": 0.92,
      "intent_preserved": true
    },
    {
      "id": "iss_a1b2c3d4-0003",
      "type": "preferred_term",
      "severity": "suggestion",
      "matched_text": "Brandguard",
      "start_offset": 11,
      "end_offset": 21,
      "reason": "Official brand spelling requires camel case 'BrandGuard'.",
      "suggested_fix": "BrandGuard",
      "source": "Brand Kit - Glossary v1.2",
      "source_id": "glossary-term-004",
      "confidence": 1.0,
      "intent_preserved": true
    }
  ]
}
```

> **Fallback Contract Guarantee (K13):**
> If Claude API times out, fails, or credentials are unconfigured, `/analyze` will ALWAYS return `200 OK` with `ai_used: false` and complete rule-based & Fact Vault heuristic issues. The UI will never receive a blank screen or 500 error on AI downtime.

---

## 4. Document & File Ingestion

### `POST /api/v1/documents/upload`
Upload a `.txt`, `.docx`, or `.pdf` file. Automatically parses and extracts clean text.

**Request:** `multipart/form-data`
- `file`: binary file
- `title`: string (optional, defaults to file name)

**Response (`201 Created`):**
```json
{
  "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Q4 Press Release.docx",
  "filename": "Q4 Press Release.docx",
  "file_type": "docx",
  "character_count": 4120,
  "extracted_text": "ApexCloud launches next generation AI security mesh..."
}
```

---

## 5. Review & Workflow Lifecycle

### Document Status Transitions:
`draft` -> `in_review` -> `approved` OR `changes_requested`

### `POST /api/v1/documents`
Create or save a new document draft.

**Request:**
```json
{
  "title": "Annual Marketing Campaign",
  "content": "Full draft content here..."
}
```

**Response (`201 Created`):**
```json
{
  "id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Annual Marketing Campaign",
  "status": "draft",
  "current_version": 1,
  "content": "Full draft content here...",
  "created_by": "usr_9f81a7b0...",
  "created_at": "2026-10-23T10:15:00.000Z",
  "updated_at": "2026-10-23T10:15:00.000Z"
}
```

---

### `GET /api/v1/documents`
List documents with optional status filtering.

**Query Parameters:**
- `status`: optional filter (`draft`, `in_review`, `approved`, `changes_requested`)
- `skip`: pagination offset (default 0)
- `limit`: pagination limit (default 20)

---

### `GET /api/v1/documents/{document_id}`
Retrieve a document with latest analysis summary and metadata.

---

### `POST /api/v1/documents/{document_id}/submit`
Submit document for reviewer approval. (Allowed for `creator` or `manager`).

**Response (`200 OK`):**
```json
{
  "id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "in_review",
  "submitted_at": "2026-10-23T11:00:00.000Z"
}
```

---

### `POST /api/v1/documents/{document_id}/approve`
Approve document. (Allowed for `manager` or `reviewer`).

**Response (`200 OK`):**
```json
{
  "id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "approved",
  "approved_by": "usr_reviewer_001",
  "approved_at": "2026-10-23T11:30:00.000Z"
}
```

---

### `POST /api/v1/documents/{document_id}/request-changes`
Request revisions with a reason. (Allowed for `manager` or `reviewer`).

**Request:**
```json
{
  "reason": "Please fix the 2 critical SLA violations and update the Q1 stats."
}
```

**Response (`200 OK`):**
```json
{
  "id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "changes_requested",
  "reason": "Please fix the 2 critical SLA violations and update the Q1 stats.",
  "reviewed_at": "2026-10-23T11:45:00.000Z"
}
```

---

### `POST /api/v1/documents/{document_id}/comments`
Add an inline or general review comment.

**Request:**
```json
{
  "content": "This paragraph should cite our Whitepaper v3 instead of claiming zero latency.",
  "start_offset": 120,
  "end_offset": 185
}
```

**Response (`201 Created`):**
```json
{
  "id": "com_82c2a931-1122",
  "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "author_id": "usr_reviewer_001",
  "author_name": "Reviewer Alice",
  "content": "This paragraph should cite our Whitepaper v3 instead of claiming zero latency.",
  "start_offset": 120,
  "end_offset": 185,
  "created_at": "2026-10-23T11:50:00.000Z"
}
```

---

### `GET /api/v1/documents/{document_id}/comments`
Retrieve all comments for a document.

---

### `GET /api/v1/documents/{document_id}/versions`
Retrieve all past content versions of a document.

---

### `GET /api/v1/documents/{document_id}/audit-log`
Retrieve immutable audit logs for compliance tracking.

**Response (`200 OK`):**
```json
[
  {
    "id": "aud_01",
    "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "action": "document_created",
    "user_id": "usr_creator",
    "user_email": "creator@brandguard.ai",
    "details": {"version": 1},
    "created_at": "2026-10-23T10:15:00.000Z"
  },
  {
    "id": "aud_02",
    "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "action": "analyzed",
    "user_id": "usr_creator",
    "user_email": "creator@brandguard.ai",
    "details": {"confidence_score": 64.0, "total_issues": 3},
    "created_at": "2026-10-23T10:16:00.000Z"
  },
  {
    "id": "aud_03",
    "document_id": "doc_3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "action": "submitted_for_review",
    "user_id": "usr_creator",
    "user_email": "creator@brandguard.ai",
    "details": {},
    "created_at": "2026-10-23T11:00:00.000Z"
  }
]
```

---

## 6. Health & System Status

### `GET /api/v1/health`
Liveness, readiness, and subsystem status.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "ai_status": "ready",
  "brand_kit_loaded": true,
  "facts_count": 12,
  "rules_count": 28,
  "timestamp": "2026-10-23T12:00:00.000Z"
}
```

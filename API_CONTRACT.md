# BrandGuard AI: API Contract (v1)

**Owner:** Kanishka (backend) · **Reviewer:** Suryansh (frontend)
**Rule:** Do not change a field name or shape without telling the other person and updating this file together.

Base URL (local): `http://localhost:8000` · All bodies are JSON · Auth: `Authorization: Bearer <token>` (skip auth until login is built)

---

## 1. Analyze content

`POST /analyze`

**Request**
```json
{
  "text": "Our app is the cheapest and fastest in India. We guarantee 100% success!",
  "content_type": "instagram_post",
  "intent": "Promote the app and create urgency"
}
```
`content_type`: `instagram_post | email | blog | ad | other`
`intent` is optional. It feeds the Intent Lock check.

**Response `200`**
```json
{
  "report_id": "rep_001",
  "status": "red",
  "masked_text": "Our app is the cheapest and fastest in India. We guarantee 100% success!",
  "pii_masked": false,
  "ai_used": true,
  "issues": [
    {
      "id": "i1",
      "type": "banned_term",
      "severity": "medium",
      "original_text": "cheapest",
      "start": 11,
      "end": 19,
      "reason": "'Cheapest' is a banned term in the brand glossary.",
      "source": { "kind": "guideline", "id": "R-01", "excerpt": "Do not use 'cheapest'. Use 'affordable'." },
      "suggested_fix": "affordable",
      "confidence": 0.98,
      "needs_human": false,
      "status": "open"
    },
    {
      "id": "i2",
      "type": "unsupported_claim",
      "severity": "high",
      "original_text": "fastest in India",
      "start": 24,
      "end": 40,
      "reason": "No approved evidence supports this superlative claim.",
      "source": { "kind": "guideline", "id": "R-02", "excerpt": "Superlatives need approved evidence." },
      "suggested_fix": "helps teams create reports quickly",
      "confidence": 0.9,
      "needs_human": false,
      "status": "open"
    },
    {
      "id": "i3",
      "type": "banned_term",
      "severity": "high",
      "original_text": "guarantee 100% success",
      "start": 45,
      "end": 67,
      "reason": "Guarantees and absolute promises are not allowed.",
      "source": { "kind": "guideline", "id": "R-03", "excerpt": "No guarantees or absolute outcomes." },
      "suggested_fix": "help you work towards your goals",
      "confidence": 0.95,
      "needs_human": true,
      "status": "open"
    }
  ],
  "summary": { "total": 3, "high": 2, "medium": 1, "low": 0 }
}
```

### Field rules
| Field | Values / meaning |
|---|---|
| `status` | `green` (no issues), `yellow` (fixable issues), `red` (high risk or needs human) |
| `type` | `banned_term`, `preferred_term`, `unsupported_claim`, `fact_mismatch`, `tone`, `pii`, `other` |
| `severity` | `low`, `medium`, `high` |
| `start` / `end` | Character positions in the **original** `text` (end is exclusive) |
| `source.kind` | `guideline` or `fact`. **Every issue must have a source.** If there is none, use `type: "other"` with `needs_human: true` and `source: null` ("needs human judgement") |
| `confidence` | 0.0 to 1.0 |
| `needs_human` | `true` means it must be routed to a reviewer |
| `status` (issue) | `open`, `accepted`, `edited`, `disputed` |
| `ai_used` | `false` if the AI call failed and only rule checks ran (fallback) |

---

## 2. Upload a file (P2)

`POST /upload` · `multipart/form-data` · fields: `file` (.docx or .pdf), `content_type`

**Response `200`**
```json
{ "text": "extracted text...", "filename": "post.docx" }
```
The frontend then sends `text` to `/analyze`.

---

## 3. Get a report

`GET /reports/{report_id}` → same shape as the `/analyze` response, plus:
```json
{ "created_by": "user_1", "created_at": "2026-10-22T10:30:00Z", "workflow_status": "draft", "final_text": null }
```
`workflow_status`: `draft | in_review | changes_requested | approved`

---

## 4. Act on a suggested fix

`POST /reports/{report_id}/issues/{issue_id}/action`

**Request**
```json
{ "action": "accept", "edited_text": null }
```
`action`: `accept | edit | dispute`
For `edit`, send `edited_text`. For `dispute`, optionally send `"note": "why"`.

**Response `200`**
```json
{ "issue_id": "i1", "status": "accepted", "current_text": "Our app is the affordable and fastest in India. ..." }
```
`current_text` is the draft after all accepted/edited fixes so far.

---

## 5. Review workflow (P2)

| Endpoint | Body | Result |
|---|---|---|
| `POST /reports/{id}/submit` | none | `workflow_status` becomes `in_review` |
| `POST /reports/{id}/approve` | `{ "comment": "..." }` | `approved`, final text locked |
| `POST /reports/{id}/request-changes` | `{ "comment": "..." }` | `changes_requested` |
| `POST /reports/{id}/comments` | `{ "text": "..." }` | adds a comment |
| `GET /reports/{id}/history` | none | list of versions, actions and who did them |

Reviewer/manager roles only for approve and request-changes.

---

## 6. Login (P2)

`POST /auth/login`
```json
{ "email": "creator@abc.com", "password": "demo123" }
```
**Response:** `{ "token": "...", "user": { "id": "user_1", "name": "Asha", "role": "creator" } }`
Roles: `creator`, `manager`, `reviewer`, `admin`.

---

## 7. Brand Kit (read-only for the demo)

`GET /brand-kit` → returns the contents of `brand_kit.json`.

---

## 8. Errors (all endpoints)

```json
{ "error": { "code": "EMPTY_TEXT", "message": "Please enter some text to check." } }
```
Codes: `EMPTY_TEXT`, `TEXT_TOO_LONG`, `UNSUPPORTED_FILE`, `NOT_FOUND`, `UNAUTHORIZED`, `AI_UNAVAILABLE`, `SERVER_ERROR`.
Messages must be readable by a normal user, because the frontend shows them as they are.

---

## Mock data for the frontend

Until the backend is ready, Suryansh uses the example response in section 1 as mock data. When the backend is live, swap the mock for the real call. The UI should not need to change.

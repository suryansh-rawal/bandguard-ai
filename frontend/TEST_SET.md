# BrandGuard AI: Test Set (v2, matches the backend Brand Kit)

Based on `backend/app/data/brand_kit.json` (BrandGuard AI, v1.2.0).
Run each text on the Analyze page, then fill the last column.

Severity in the backend: critical (shown as high), warning (medium), suggestion (low).

## Content tests

| # | Case | Content type | Text | Expected issues | Result (Pass / Fail + notes) |
|---|---|---|---|---|---|
| T1 | Clean post | instagram_post | BrandGuard AI helps enterprise teams review content before it goes live. | None. Status green | |
| T2 | Banned word (suggestion) | ad | Our platform is the cheapest option for teams. | BAN-003 "cheapest" → "cost-effective" | |
| T3 | Absolute claims (critical) | ad | BrandGuard AI is unhackable and never fails. | BAN-002 "unhackable", BAN-009 "never fails". Both critical, shown as needs human review | |
| T4 | Hyperbole (warning) | blog | This foolproof tool works like magic. | BAN-005 "foolproof", BAN-004 "works like magic" | |
| T5 | Superlative and guarantee | ad | We are the fastest in India. We guarantee 100% success! | BAN-012 "fastest in India", BAN-011 "guarantee 100% success" | |
| T6 | Preferred terms | email | Brandguard is an AI powered work space. Log on today. | PREF-001 "Brandguard", PREF-002 "AI powered", PREF-005 "work space", PREF-004 "Log on" | |
| T7 | Fact check | instagram_post | We serve over 50,000 enterprise teams with 99.99% uptime. | Should be flagged against Fact Vault FV-003 (10,000 teams) and FV-001 (99.95% uptime). Note what the backend actually returns | |
| T8 | Sensitive data | email | Please contact Priya Sharma at priya@gmail.com or 9876543210. | Should be flagged as private data (name, email, phone). Note what the backend actually returns | |

T1 to T6 were checked against the Brand Kit patterns. T7 and T8 depend on the backend logic, so write down what really happens.

## Error and edge tests

| # | Case | What to do | Expected | Result |
|---|---|---|---|---|
| E1 | Empty text | Leave the box empty, press Check | Message "Please enter some text to check." | |
| E2 | Backend off | Stop the backend, press Check | Message "Could not reach the server..." | |
| E3 | Very long text | Paste about 10,000 words | Readable error or a normal result. No freeze | |
| E4 | Upload .docx | Upload a small Word file | Text appears in the box | |
| E5 | Upload .pdf | Upload a small PDF | Text appears in the box | |
| E6 | Wrong file type | Upload a .png | Readable error | |

## UI checks (every run)

- Issue cards show original text, reason, source id and name, suggested fix, Accept / Edit / Dispute.
- Highlights in Before match the issue text. After changes when Accept / Edit / Dispute is clicked.
- Status badge and issue counts are correct.
- Critical issues show "Needs human review".
- No "Demo data" banner when `VITE_USE_MOCK=false`.

## Bug log

| Bug | Where | What happened | Expected | Status |
|---|---|---|---|---|
| Backend route prefix | Backend | Routes are under /api/v1, contract says no prefix | Contract and backend agree | Handled in frontend |
| Response field names | Backend | matched_text, start_offset, severity names differ from contract | Contract names | Adapter in api.js |
| Missing rules | Backend kit | "fastest" and "guarantee 100% success" were not caught | Both flagged | Fixed (BAN-011, BAN-012) |
| Upload route | Backend | /documents/upload instead of /upload | One agreed route | Open |
| Accept / Edit / Dispute save | Backend | No matching route found | Action saved by backend | Open |
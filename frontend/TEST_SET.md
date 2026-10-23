# BrandGuard AI: Test Set

Based on `API_CONTRACT.md` and `brand_kit.json` (ABC App sample data).
Run each text on the Analyze page with the stated content type. Fill the last column after each run.

Reference facts: F-01 = 10 languages, F-03 = more than 500 teams, F-04 = plans start at Rs 549/month, F-05 = 30% faster report prep (internal benchmark of 40 teams).

## Content tests

| # | Case | Content type | Text | Expected status | Expected issues | Result (Pass / Fail + notes) |
|---|---|---|---|---|---|---|
| T1 | Clean post | instagram_post | ABC App helps teams create reports quickly. Plans start at Rs 549 per month. | green | None | |
| T2 | Banned word | ad | ABC App is the cheapest way to build reports. Try it today. | yellow | 1 issue, `banned_term`: "cheapest", source R-01, fix "affordable" | |
| T3 | Unsupported claim | ad | ABC App is the fastest and number one reporting app in India. | red | `unsupported_claim` on "fastest" and on "number one", source R-02 (superlatives need evidence), severity high | |
| T4 | Fact mismatch | instagram_post | ABC App supports 25 languages, is used by 2,000 teams, and plans start at Rs 499 per month. | red | 3 x `fact_mismatch`: "25 languages" (F-01 says 10), "2,000 teams" (F-03 says more than 500), "Rs 499" (F-04 says Rs 549). Each has `source.kind = fact` | |
| T5 | Tone | email | Hey guys!! Our new feature is gonna be insane lol! | yellow | `tone` issues for slang ("guys", "gonna", "insane", "lol") and too many exclamation marks (R-07). Severity low | |
| T6 | Guarantee | ad | We guarantee 100% success with ABC App! | red | `banned_term` on "guarantee 100% success", source R-03, severity high, `needs_human` true | |
| T7 | Sensitive data | instagram_post | Thank you Priya Sharma (priya@gmail.com, 9876543210) for loving ABC App! | red | `pii` issue(s), source R-05. `pii_masked` is true and `masked_text` shows [NAME], [EMAIL], [PHONE] | |

## Error and edge tests

| # | Case | What to do | Expected | Result |
|---|---|---|---|---|
| E1 | Empty text | Leave the box empty, press Check | Message "Please enter some text to check." No crash | |
| E2 | Backend off | Stop the backend, press Check | Message "Could not reach the server..." No blank page | |
| E3 | Very long text | Paste about 10,000 words | Readable error (TEXT_TOO_LONG) or a normal result. No freeze | |
| E4 | Upload .docx | Upload a small Word file | Text appears in the box, then Check works | |
| E5 | Upload .pdf | Upload a small PDF | Text appears in the box, then Check works | |
| E6 | Wrong file type | Upload a .png | Readable error (UNSUPPORTED_FILE) | |

## UI checks (every run)

- Each issue card shows the original text, reason, source (id and excerpt), suggested fix, and Accept / Edit / Dispute.
- Highlighted text in Before matches `start` and `end` from the response.
- After text changes when Accept / Edit / Dispute is clicked.
- Status badge matches `status` (green / yellow / red).
- Issues with `needs_human = true` show "Needs human review".
- If `ai_used` is false, the warning banner appears.
- No "Demo data" banner once `VITE_USE_MOCK=false`.

## Bug log

| Bug | Page | What happened | Expected | Status |
|---|---|---|---|---|
| | | | | |

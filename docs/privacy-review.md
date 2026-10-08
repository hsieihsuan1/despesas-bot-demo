# Privacy review: curated local demo

## Data boundary

Only invented expense descriptions, categories, cent amounts and dates are seeded or shown. No person names, addresses, account numbers, balances, portfolio positions, financial documents, chat IDs or user IDs are in the candidate.

The app runs without credentials and makes no outbound service calls. The browser calls only its local server. The ledger is in memory, resets on process restart, and is not logged by request handlers. The optional file-path parameter in the reusable ledger class is not used by the demo server. The UI uses textContent for returned strings.

## Excluded original paths

No Telegram adapter, webhook/polling service, Google Sheets adapter, service-account loader, Gemini call, LangSmith tracing, FinOps sender, bank/PDF/image/voice parser, investment recommendation or billing/metrics inspector was ported. The tracked session pickle was neither downloaded nor deserialized. All original operational documentation and personal deployment references were replaced, not copied.

The original source enabled tracing by default and had globally configured Sheets access. That is a privacy-design risk to review for any future live version, not evidence of a demonstrated disclosure or breach. This local demo does not establish the original service's security or exactly-once delivery.

## Remaining limits

No auth, user isolation or real data protections. Loopback binding and Origin checks are demo controls only; they do not defend against every local process or client. The app is meant for one synthetic session on a trusted machine. If a real service is later added, assess Telegram identity, scoped storage, provider retention/tracing consent, secure secret storage, encryption, deletion/export, backups and authorization tests before use.

A heuristic scan and manual curated-file review found no credentials/personal identifiers in the release tree. This is not a complete security audit or a guarantee that automated scans detect every secret.

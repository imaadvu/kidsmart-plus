Privacy & Compliance (AU Context)

Scope
- Collect only publicly available program listings for educational purposes.
- Respect robots.txt and site Terms of Service (TOS).

Controls
- Provenance ledger per record: robots_ok, crawl_delay, first_seen, last_seen, checksum.
- Snapshots store minimal HTML excerpts for audit; support takedown/deletion on request.
- Secrets via .env; no hardcoded API keys.
- Access control with JWT and roles; audit logging for admin actions.
- Output sanitization and HTML escaping in dashboard.

References (as cited in prior proposals)
- Australian Privacy Principles (APPs) under the Privacy Act 1988.
- Department of Education guidance on handling student-related data (public information only).
- Local government guidelines for web scraping of public data respecting robots.txt and TOS.

Data Subject Rights
- Remove snapshots upon valid takedown request.
- Provide source URL and provenance metadata in exports.

Retention
- Store program snapshots for audit with minimal content and delete when obsolete or upon request.


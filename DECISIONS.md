# Decisions

| Date | Decision | Reason | Alternatives considered |
|---|---|---|---|
| 2026-09-13 | Use a monorepo instead of splitting into multiple repos | The tracker dataset is shared by multiple tools (site build, tag generator, monitoring) — splitting it would require cross-repo versioning and sync | Separate data repo + separate site repo |
| 2026-09-13 | Build a purely static site, not WordPress or another CMS | Avoids a dual source of truth and preserves a continuous, auditable version history in git | WordPress/headless CMS with a database of record |
| 2026-09-13 | Record enforcement mechanism, not penalty amounts | Most penalties are set by national implementing law rather than the instrument itself; a single figure would misrepresent the real range | Publishing a single penalty amount or range per entry regardless of source |
| 2026-09-13 | Structured fields are fully bilingual; long-form content is translated selectively | Structured fields change rarely, so translation cost is low; long-form articles go stale quickly and translating all of them isn't sustainable | Fully bilingual site including all articles; English-only site |
| 2026-09-13 | Entry `id` is never modified; superseding regulations get a new entry | Protects external links and citations to existing ids from breaking | Editing the existing entry in place when a regulation is replaced |
| 2026-09-13 | Add `GCC` as a jurisdiction value, and add an `applies_in` field | A GCC technical regulation (e.g. BD-142004-01) applies to seven member states as a single instrument; duplicating an entry per country would cause maintenance drift. A single entry plus `applies_in` expresses the scope, and the frontend filter matches against `applies_in` as well. | Duplicate the entry per country (rejected — causes drift) |
| 2026-09-13 | Add a `review_status` field | Allows automated extraction to populate entries quickly to speed up initial buildout, while preserving traceability of whether a human has actually verified the content — avoids diluting the meaning of `last_reviewed` | Only write entries after human review is complete (rejected — would slow down the initial version) |

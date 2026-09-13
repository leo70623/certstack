# CertStack — Project Context

## Purpose

CertStack tracks global regulatory requirements for consumer electronics
products across nine jurisdictions:

- EU (European Union)
- UK (United Kingdom)
- US (United States)
- CN (China)
- KR (South Korea)
- JP (Japan)
- SA (Saudi Arabia)
- AE (United Arab Emirates)
- ZA (South Africa)

## Scope

The scope is limited to regulations affecting consumer electronics products
(and closely related components: power supplies, batteries, cables/connectors,
packaging, software/firmware) — not general product safety or unrelated
industries.

## Structure

- The **tracker** (`data/tracker.yml`) is the primary content type: a
  structured, machine-readable table of regulatory entries.
- **Articles** (`content/articles/`) are secondary: narrative interpretation
  and explanation, written in support of the tracker, not a replacement for
  it.
- A tag generator tool (`tools/garan/`) assists with tagging content.

## Source of truth

This repository is the single source of truth. The published website is a
rendering layer only — it has no independent state, and all edits are made
in this repo.

## Data honesty principles

- `last_verified` and `last_reviewed` must be displayed on the frontend for
  every entry. Do not hide these dates.
- Entries with `confidence: medium` or `confidence: low` must be visibly
  flagged in the UI — do not present them with the same visual weight as
  `confidence: high` entries.
- Penalty fields record the **enforcement mechanism**, not a monetary amount.
  Most penalties are set by national implementing law, not the instrument
  itself, so a single number would misrepresent reality. Only
  `enforcement.penalty_range` may contain a figure, and only when the
  original regulatory text specifies a single fixed amount.
- Entries with `review_status: pending` must display a clear indicator on
  the frontend, with the label "待人工複核 / Pending human review". This is
  required in addition to (not instead of) the `confidence` flag above.

## Content discipline

- Regulatory instrument text itself may be freely quoted/cited.
- Standards text (GB, EN, ISO, and similar) must **not** be reproduced —
  no clauses, tables, or limit values copied from standard bodies' texts.
- Entries with `instrument_type: mandatory_standard` record structured
  fields only. Do not write content summaries for these entries.
- A real regulation id must never be bound to unverified field values.
  Template or placeholder entries must always use an `example-` prefixed
  id and a citation clearly marked as a placeholder. Any field value that
  has not been manually verified word-for-word against the official source
  must not be entered into an entry with a real regulation id.

## Language strategy

- All structured tracker fields are fully bilingual (en/zh required).
- Long-form content (articles) is translated selectively, not by default —
  translation cost is high and long text goes stale quickly, while
  structured fields change rarely and are cheap to keep bilingual.

## URL structure

- `/en/reg/<id>` — English regulation entry page
- `/zh/reg/<id>` — Chinese regulation entry page
- `/en/guides/<slug>` — English guide/article
- `/zh/guides/<slug>` — Chinese guide/article
- Supranational-level entries (`jurisdiction: GCC` or `EU`) use their own
  jurisdiction in the URL (e.g. `/en/reg/gcc-bd-142004-01`) and are not
  duplicated per member state.

#!/usr/bin/env python3
"""Validate data/tracker.yml against data/schema.yml and data/vocab.yml."""

import sys
import re
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TRACKER_FILE = DATA / "tracker.yml"
SCHEMA_FILE = DATA / "schema.yml"
VOCAB_FILE = DATA / "vocab.yml"

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

JURISDICTIONS = {"EU", "UK", "US", "CN", "KR", "JP", "SA", "AE", "ZA",
                  "GCC", "KW", "QA", "BH", "OM"}
APPLIES_IN_VALUES = JURISDICTIONS - {"GCC", "EU"}

errors = []
warnings = []


def err(entry_id, field, message):
    errors.append(f"{TRACKER_FILE.name}:{entry_id}:{field}:{message}")


def warn(entry_id, field, message):
    warnings.append(f"{TRACKER_FILE.name}:{entry_id}:{field}:{message}")


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_bilingual(value):
    return (
        isinstance(value, dict)
        and set(value.keys()) >= {"en", "zh"}
        and isinstance(value.get("en"), str)
        and isinstance(value.get("zh"), str)
    )


def check_bilingual(entry_id, field, value, required):
    if value is None:
        if required:
            err(entry_id, field, "missing required bilingual field")
        return
    if not is_bilingual(value):
        err(entry_id, field, "bilingual field must have 'en' and 'zh' string keys")
        return
    if not value["en"].strip():
        err(entry_id, field, "en value must not be empty")
    if not value["zh"].strip():
        err(entry_id, field, "zh value must not be empty")


def check_date(entry_id, field, value, required):
    if value is None:
        if required:
            err(entry_id, field, "missing required date")
        return
    if isinstance(value, date) and not isinstance(value, datetime):
        return
    if isinstance(value, str):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return
        except ValueError:
            pass
    err(entry_id, field, f"invalid date value: {value!r}")


def to_date(value):
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


def check_enum(entry_id, field, value, allowed, required):
    if value is None:
        if required:
            err(entry_id, field, "missing required value")
        return
    if value not in allowed:
        err(entry_id, field, f"invalid enum value {value!r}, expected one of {allowed}")


def main():
    schema = load_yaml(SCHEMA_FILE)  # noqa: F841 (kept for future schema-driven validation)
    vocab = load_yaml(VOCAB_FILE)
    tracker = load_yaml(TRACKER_FILE) or []

    valid_product_tags = set(vocab.get("product_tags", {}).keys())
    valid_component_tags = set(vocab.get("component_tags", {}).keys())

    ids_seen = set()
    entries_by_id = {}
    duplicate_ids = set()

    for entry in tracker:
        eid = entry.get("id")
        if eid in ids_seen:
            duplicate_ids.add(eid)
        ids_seen.add(eid)
        entries_by_id[eid] = entry

    today = date.today()

    for entry in tracker:
        eid = entry.get("id", "<missing-id>")

        # id
        if not entry.get("id"):
            err(eid, "id", "id is required")
        elif not ID_PATTERN.match(entry["id"]):
            err(eid, "id", f"id {entry['id']!r} does not match pattern {ID_PATTERN.pattern}")
        if eid in duplicate_ids:
            err(eid, "id", "id is not unique")
        if isinstance(eid, str) and eid.startswith("example-"):
            warn(eid, "id", "this is a template/placeholder entry")

        # jurisdiction
        jurisdiction = entry.get("jurisdiction")
        check_enum(eid, "jurisdiction", jurisdiction, JURISDICTIONS, True)

        # applies_in
        applies_in = entry.get("applies_in") or []
        for code in applies_in:
            if code not in APPLIES_IN_VALUES:
                err(eid, "applies_in",
                    f"invalid applies_in value {code!r}, must be a country code "
                    f"other than GCC or EU")
        if jurisdiction == "GCC":
            if not applies_in:
                err(eid, "applies_in", "required and must have at least one item when jurisdiction is GCC")
        elif jurisdiction != "EU":
            if applies_in:
                err(eid, "applies_in", "must be empty unless jurisdiction is GCC or EU")

        # citation / local_type
        if not entry.get("citation"):
            err(eid, "citation", "citation is required")
        if not entry.get("local_type"):
            err(eid, "local_type", "local_type is required")

        # instrument_type
        check_enum(eid, "instrument_type", entry.get("instrument_type"),
                   {"regulation", "directive", "mandatory_standard",
                    "administrative_measure", "guidance", "statute"}, True)

        # short_name
        check_bilingual(eid, "short_name", entry.get("short_name"), True)

        # product_scope
        check_bilingual(eid, "product_scope", entry.get("product_scope"), True)

        # product_tags
        product_tags = entry.get("product_tags") or []
        if not product_tags:
            err(eid, "product_tags", "at least one product_tag is required")
        for tag in product_tags:
            if tag not in valid_product_tags:
                err(eid, "product_tags", f"unknown product_tag {tag!r}")

        # component_tags
        for tag in entry.get("component_tags") or []:
            if tag not in valid_component_tags:
                err(eid, "component_tags", f"unknown component_tag {tag!r}")

        # applies_to
        for actor in entry.get("applies_to") or []:
            if actor not in {"producer", "seller", "importer", "manufacturer"}:
                err(eid, "applies_to", f"invalid actor {actor!r}")

        # status
        status = entry.get("status")
        check_enum(eid, "status", status,
                   {"draft", "adopted", "in_force", "superseded", "withdrawn"}, True)

        # parent
        parent = entry.get("parent")
        if "parent" not in entry:
            err(eid, "parent", "parent is required (use null if none)")
        elif parent is not None:
            if parent not in entries_by_id:
                err(eid, "parent", f"parent {parent!r} does not exist")
            elif entries_by_id[parent].get("parent") is not None:
                err(eid, "parent", "parent chains of more than one level are not allowed")

        # superseded_by / status coupling
        superseded_by = entry.get("superseded_by")
        if status == "superseded":
            if not superseded_by:
                err(eid, "superseded_by", "required when status is superseded")
        else:
            if superseded_by is not None:
                err(eid, "superseded_by", "must be null unless status is superseded")
        if superseded_by is not None and superseded_by not in entries_by_id:
            err(eid, "superseded_by", f"superseded_by {superseded_by!r} does not exist")

        # related
        for rel in entry.get("related") or []:
            if rel not in entries_by_id:
                err(eid, "related", f"related id {rel!r} does not exist")

        # dates
        dates = entry.get("dates") or {}
        check_date(eid, "dates.published", dates.get("published"), True)
        check_date(eid, "dates.application", dates.get("application"), True)
        check_date(eid, "dates.labelling", dates.get("labelling"), False)
        check_date(eid, "dates.transition_end", dates.get("transition_end"), False)

        # requirements
        requirements = entry.get("requirements") or {}
        for bfield in ("marking", "local_representative", "local_testing", "registration"):
            if not isinstance(requirements.get(bfield), bool):
                err(eid, f"requirements.{bfield}", "must be a boolean and is required")
        check_enum(eid, "requirements.conformity_assessment",
                   requirements.get("conformity_assessment"),
                   {"none", "sdoc", "ccc", "type_approval", "third_party",
                    "sdoc_or_certification"}, True)

        # obligations
        obligations = entry.get("obligations") or []
        if not obligations:
            err(eid, "obligations", "at least one obligation is required")
        for i, ob in enumerate(obligations):
            actor = ob.get("actor")
            if actor not in {"producer", "seller", "importer", "manufacturer"}:
                err(eid, f"obligations[{i}].actor", f"invalid actor {actor!r}")
            check_bilingual(eid, f"obligations[{i}].action", ob.get("action"), True)

        # sources
        sources = entry.get("sources") or []
        if not sources:
            err(eid, "sources", "at least one source is required")
        for i, src in enumerate(sources):
            if not src.get("url"):
                err(eid, f"sources[{i}].url", "url is required")
            check_enum(eid, f"sources[{i}].type", src.get("type"), {"primary", "secondary"}, True)
            if not src.get("publisher"):
                err(eid, f"sources[{i}].publisher", "publisher is required")

        # enforcement
        enforcement = entry.get("enforcement") or {}
        if not enforcement.get("authority"):
            err(eid, "enforcement.authority", "authority is required")
        if not enforcement.get("mechanism"):
            err(eid, "enforcement.mechanism", "mechanism is required")
        check_enum(eid, "enforcement.penalty_basis", enforcement.get("penalty_basis"),
                   {"in_instrument", "national_law", "none_specified"}, True)
        check_bilingual(eid, "enforcement.penalty_summary",
                         enforcement.get("penalty_summary"), True)
        source_ref = enforcement.get("source_ref")
        if source_ref is not None:
            if not isinstance(source_ref, int) or not (0 <= source_ref < len(sources)):
                err(eid, "enforcement.source_ref",
                    f"source_ref {source_ref!r} out of range for sources list")
        check_date(eid, "enforcement.last_verified", enforcement.get("last_verified"), True)

        # monitoring
        monitoring = entry.get("monitoring") or {}
        tier = monitoring.get("tier")
        check_enum(eid, "monitoring.tier", tier, {"A", "B", "C"}, True)
        method = monitoring.get("method")
        check_enum(eid, "monitoring.method", method, {"rss", "api", "page_diff", "manual"}, True)
        check_enum(eid, "monitoring.frequency", monitoring.get("frequency"),
                   {"daily", "weekly", "quarterly"}, True)
        if tier == "A" and method == "manual":
            err(eid, "monitoring.method", "tier A entries must not use manual monitoring")

        # last_verified / last_reviewed
        last_verified = entry.get("last_verified")
        last_reviewed = entry.get("last_reviewed")
        check_date(eid, "last_verified", last_verified, True)
        check_date(eid, "last_reviewed", last_reviewed, True)
        lv = to_date(last_verified)
        lr = to_date(last_reviewed)
        if lv and lr and lr > lv:
            err(eid, "last_reviewed", "last_reviewed must not be later than last_verified")
        if lv and lv > today:
            err(eid, "last_verified", "last_verified must not be in the future")

        # confidence
        confidence = entry.get("confidence")
        check_enum(eid, "confidence", confidence, {"high", "medium", "low"}, True)

        # review_status
        review_status = entry.get("review_status")
        check_enum(eid, "review_status", review_status, {"pending", "reviewed"}, True)
        if review_status == "pending":
            if confidence == "high":
                err(eid, "confidence", "confidence must not be high while review_status is pending")
            warn(eid, "review_status", "entry is pending human review")

        # notes (optional bilingual)
        if entry.get("notes") is not None:
            check_bilingual(eid, "notes", entry.get("notes"), False)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n{len(errors)} error(s) found.", file=sys.stderr)
        sys.exit(1)

    print(f"OK: {len(tracker)} entr{'y' if len(tracker) == 1 else 'ies'} validated, no errors.")
    sys.exit(0)


if __name__ == "__main__":
    main()

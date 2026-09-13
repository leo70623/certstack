#!/usr/bin/env python3
"""依 data/schema.yml 與 data/vocab.yml 驗證 data/tracker.yml。"""

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


def check_bilingual(entry_id, field, container, key, required, nullable=False):
    """required 判斷 `key` 是否必須存在於 `container` 中。
    nullable 判斷當 key 存在但值為 None 時是否合法
    （即該欄位的 schema 型別為 bilingual_or_null）。"""
    present = key in container
    value = container.get(key)
    if not present:
        if required:
            err(entry_id, field, "缺少必填的雙語欄位")
        return
    if value is None:
        if not nullable:
            err(entry_id, field, "值不得為 null")
        return
    if not is_bilingual(value):
        err(entry_id, field, "雙語欄位必須同時具備 'en' 與 'zh' 字串鍵值")
        return
    if not value["en"].strip():
        err(entry_id, field, "en 值不得為空")
    if not value["zh"].strip():
        err(entry_id, field, "zh 值不得為空")


def check_date(entry_id, field, container, key, required, nullable=False):
    """required 判斷 `key` 是否必須存在於 `container` 中。
    nullable 判斷當 key 存在但值為 None 時是否合法
    （即該欄位的 schema 型別為 date_or_null）。"""
    present = key in container
    value = container.get(key)
    if not present:
        if required:
            err(entry_id, field, "缺少必填日期欄位")
        return
    if value is None:
        if not nullable:
            err(entry_id, field, "值不得為 null")
        return
    if isinstance(value, date) and not isinstance(value, datetime):
        return
    if isinstance(value, str):
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return
        except ValueError:
            pass
    err(entry_id, field, f"日期值無效：{value!r}")


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
            err(entry_id, field, "缺少必填值")
        return
    if value not in allowed:
        err(entry_id, field, f"enum 值無效：{value!r}，應為下列其中之一：{allowed}")


def main():
    schema = load_yaml(SCHEMA_FILE)  # noqa: F841（保留供未來改為 schema 驅動驗證使用）
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
            err(eid, "id", "id 為必填")
        elif not ID_PATTERN.match(entry["id"]):
            err(eid, "id", f"id {entry['id']!r} 不符合格式 {ID_PATTERN.pattern}")
        if eid in duplicate_ids:
            err(eid, "id", "id 重複，必須唯一")
        if isinstance(eid, str) and eid.startswith("example-"):
            warn(eid, "id", "此為範本／佔位條目")

        # jurisdiction
        jurisdiction = entry.get("jurisdiction")
        check_enum(eid, "jurisdiction", jurisdiction, JURISDICTIONS, True)

        # applies_in
        applies_in = entry.get("applies_in") or []
        for code in applies_in:
            if code not in APPLIES_IN_VALUES:
                err(eid, "applies_in",
                    f"applies_in 值無效：{code!r}，必須是國家代碼，且不得為 GCC 或 EU")
        if jurisdiction == "GCC":
            if not applies_in:
                err(eid, "applies_in", "jurisdiction 為 GCC 時，applies_in 為必填且至少須有一項")
        elif jurisdiction != "EU":
            if applies_in:
                err(eid, "applies_in", "除非 jurisdiction 為 GCC 或 EU，否則 applies_in 必須為空")

        # citation / local_type
        if not entry.get("citation"):
            err(eid, "citation", "citation 為必填")
        if not entry.get("local_type"):
            err(eid, "local_type", "local_type 為必填")

        # instrument_type
        check_enum(eid, "instrument_type", entry.get("instrument_type"),
                   {"regulation", "directive", "mandatory_standard",
                    "administrative_measure", "guidance", "statute"}, True)

        # short_name
        check_bilingual(eid, "short_name", entry, "short_name", True)

        # product_scope
        check_bilingual(eid, "product_scope", entry, "product_scope", True)

        # product_tags
        product_tags = entry.get("product_tags") or []
        if not product_tags:
            err(eid, "product_tags", "至少須有一個 product_tag")
        for tag in product_tags:
            if tag not in valid_product_tags:
                err(eid, "product_tags", f"未知的 product_tag：{tag!r}")

        # component_tags
        for tag in entry.get("component_tags") or []:
            if tag not in valid_component_tags:
                err(eid, "component_tags", f"未知的 component_tag：{tag!r}")

        # applies_to
        for actor in entry.get("applies_to") or []:
            if actor not in {"producer", "seller", "importer", "manufacturer"}:
                err(eid, "applies_to", f"actor 無效：{actor!r}")

        # status
        status = entry.get("status")
        check_enum(eid, "status", status,
                   {"draft", "adopted", "in_force", "superseded", "withdrawn"}, True)

        # parent
        parent = entry.get("parent")
        if "parent" not in entry:
            err(eid, "parent", "parent 為必填（無上層條目請填 null）")
        elif parent is not None:
            if parent not in entries_by_id:
                err(eid, "parent", f"parent {parent!r} 不存在")
            elif entries_by_id[parent].get("parent") is not None:
                err(eid, "parent", "不允許超過一層的 parent 鏈")

        # superseded_by / status coupling
        superseded_by = entry.get("superseded_by")
        if status == "superseded":
            if not superseded_by:
                err(eid, "superseded_by", "status 為 superseded 時為必填")
        else:
            if superseded_by is not None:
                err(eid, "superseded_by", "status 非 superseded 時必須為 null")
        if superseded_by is not None and superseded_by not in entries_by_id:
            err(eid, "superseded_by", f"superseded_by {superseded_by!r} 不存在")

        # related
        for rel in entry.get("related") or []:
            if rel not in entries_by_id:
                err(eid, "related", f"related id {rel!r} 不存在")

        # dates
        dates = entry.get("dates") or {}
        check_date(eid, "dates.published", dates, "published", True, nullable=True)
        check_date(eid, "dates.application", dates, "application", True)
        check_date(eid, "dates.labelling", dates, "labelling", False, nullable=True)
        check_date(eid, "dates.transition_end", dates, "transition_end", False, nullable=True)

        # requirements
        requirements = entry.get("requirements") or {}
        for bfield in ("marking", "local_representative", "local_testing", "registration"):
            if not isinstance(requirements.get(bfield), bool):
                err(eid, f"requirements.{bfield}", "必須為布林值，且為必填")
        conformity_assessment = requirements.get("conformity_assessment")
        ca_allowed = {"none", "sdoc", "ccc", "type_approval", "third_party"}
        if not isinstance(conformity_assessment, list) or not conformity_assessment:
            err(eid, "requirements.conformity_assessment",
                "必須為非空的 enum 值 list")
        else:
            for value in conformity_assessment:
                if value not in ca_allowed:
                    err(eid, "requirements.conformity_assessment",
                        f"enum 值無效：{value!r}，應為下列其中之一：{ca_allowed}")
            if len(conformity_assessment) != len(set(conformity_assessment)):
                err(eid, "requirements.conformity_assessment",
                    "不得包含重複值")
            if "none" in conformity_assessment and len(conformity_assessment) > 1:
                err(eid, "requirements.conformity_assessment",
                    "'none' 不得與其他值並存")
            if len(conformity_assessment) > 1:
                check_bilingual(eid, "requirements.conformity_assessment_note",
                                 requirements, "conformity_assessment_note", True)

        # obligations
        obligations = entry.get("obligations") or []
        if not obligations:
            err(eid, "obligations", "至少須有一項 obligation")
        for i, ob in enumerate(obligations):
            actor = ob.get("actor")
            if actor not in {"producer", "seller", "importer", "manufacturer"}:
                err(eid, f"obligations[{i}].actor", f"actor 無效：{actor!r}")
            check_bilingual(eid, f"obligations[{i}].action", ob, "action", True)

        # sources
        sources = entry.get("sources") or []
        if not sources:
            err(eid, "sources", "至少須有一個 source")
        for i, src in enumerate(sources):
            if not src.get("url"):
                err(eid, f"sources[{i}].url", "url 為必填")
            check_enum(eid, f"sources[{i}].type", src.get("type"), {"primary", "secondary"}, True)
            if not src.get("publisher"):
                err(eid, f"sources[{i}].publisher", "publisher 為必填")

        # enforcement
        enforcement = entry.get("enforcement") or {}
        if not enforcement.get("authority"):
            err(eid, "enforcement.authority", "authority 為必填")
        if not enforcement.get("mechanism"):
            err(eid, "enforcement.mechanism", "mechanism 為必填")
        check_enum(eid, "enforcement.penalty_basis", enforcement.get("penalty_basis"),
                   {"in_instrument", "national_law", "none_specified"}, True)
        check_bilingual(eid, "enforcement.penalty_summary",
                         enforcement, "penalty_summary", True)
        source_ref = enforcement.get("source_ref")
        if source_ref is not None:
            if not isinstance(source_ref, int) or not (0 <= source_ref < len(sources)):
                err(eid, "enforcement.source_ref",
                    f"source_ref {source_ref!r} 超出 sources 清單範圍")
        check_date(eid, "enforcement.last_verified", enforcement, "last_verified", True)

        # monitoring
        monitoring = entry.get("monitoring") or {}
        tier = monitoring.get("tier")
        check_enum(eid, "monitoring.tier", tier, {"A", "B", "C"}, True)
        method = monitoring.get("method")
        check_enum(eid, "monitoring.method", method, {"rss", "api", "page_diff", "manual"}, True)
        check_enum(eid, "monitoring.frequency", monitoring.get("frequency"),
                   {"daily", "weekly", "quarterly"}, True)
        if tier == "A" and method == "manual":
            err(eid, "monitoring.method", "tier 為 A 的條目不得使用 manual 監控方式")

        # last_verified / last_reviewed
        last_verified = entry.get("last_verified")
        last_reviewed = entry.get("last_reviewed")
        check_date(eid, "last_verified", entry, "last_verified", True)
        check_date(eid, "last_reviewed", entry, "last_reviewed", True)
        lv = to_date(last_verified)
        lr = to_date(last_reviewed)
        if lv and lr and lr > lv:
            err(eid, "last_reviewed", "last_reviewed 不得晚於 last_verified")
        if lv and lv > today:
            err(eid, "last_verified", "last_verified 不得晚於今日")

        # confidence
        confidence = entry.get("confidence")
        check_enum(eid, "confidence", confidence, {"high", "medium", "low"}, True)

        # review_status
        review_status = entry.get("review_status")
        check_enum(eid, "review_status", review_status, {"pending", "reviewed"}, True)
        if review_status == "pending":
            if confidence == "high":
                err(eid, "confidence", "review_status 為 pending 時，confidence 不得為 high")
            warn(eid, "review_status", "此條目待人工複核")

        # notes（選填雙語欄位，允許 key 存在但值為 null）
        check_bilingual(eid, "notes", entry, "notes", False, nullable=True)

    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"\n共發現 {len(errors)} 項錯誤。", file=sys.stderr)
        sys.exit(1)

    print(f"OK：已驗證 {len(tracker)} 筆條目，無錯誤。")
    sys.exit(0)


if __name__ == "__main__":
    main()

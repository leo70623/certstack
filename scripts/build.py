#!/usr/bin/env python3
"""Build site/data.json from data/tracker.yml and data/vocab.yml.

Bilingual structures are preserved as-is (e.g. {"en": ..., "zh": ...}) so the
frontend can select the active language at render time.
"""

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TRACKER_FILE = DATA / "tracker.yml"
VOCAB_FILE = DATA / "vocab.yml"
OUTPUT_FILE = ROOT / "site" / "data.json"


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def default_json(obj):
    # yaml.safe_load returns datetime.date objects for unquoted dates;
    # serialize them as ISO strings for JSON.
    return obj.isoformat()


def main():
    tracker = load_yaml(TRACKER_FILE) or []
    vocab = load_yaml(VOCAB_FILE) or {}

    output = {
        "vocab": vocab,
        "entries": tracker,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=default_json)
        f.write("\n")

    print(f"Wrote {OUTPUT_FILE} ({len(tracker)} entries).")


if __name__ == "__main__":
    main()

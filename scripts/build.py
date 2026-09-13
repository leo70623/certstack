#!/usr/bin/env python3
"""依 data/tracker.yml 與 data/vocab.yml 建置 site/data.json。

雙語結構原樣保留（例如 {"en": ..., "zh": ...}），
讓前端可以在渲染時自行選擇要顯示的語言。
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
    # yaml.safe_load 對未加引號的日期會回傳 datetime.date 物件，
    # 這裡將其序列化為 ISO 格式字串以便輸出 JSON。
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

    print(f"已寫入 {OUTPUT_FILE}（共 {len(tracker)} 筆條目）。")


if __name__ == "__main__":
    main()

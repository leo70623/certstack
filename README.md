# CertStack

消費性電子產品的全球法規追蹤站，涵蓋九個法域：EU、UK、US、CN、KR、JP、SA、AE、ZA。

範疇與原則請見 [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md)，
架構決策紀錄請見 [`DECISIONS.md`](DECISIONS.md)。

## 目錄結構

- `data/` — 欄位定義（`schema.yml`）、控制詞彙表（`vocab.yml`），以及
  法規追蹤資料集（`tracker.yml`）
- `content/` — 雙語文章與共用內容片段
- `site/` — 靜態前端（單檔 HTML + vanilla JS）
- `tools/garan/` — 標籤產生器工具
- `monitor/` — 法規來源監測設定
- `scripts/` — 建置與驗證工具（Python 3，僅用標準庫 + PyYAML）

## 環境需求

- Python 3
- PyYAML（`pip install PyYAML`）

## 使用方式

驗證追蹤資料集：

```sh
python3 scripts/validate.py
```

由追蹤資料集建置 `site/data.json`：

```sh
python3 scripts/build.py
```

## 部署

`site/` 目錄以靜態網站形式部署至 Cloudflare Pages。

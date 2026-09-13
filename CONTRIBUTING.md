# 協作慣例

本文件規定 CertStack 專案中，哪些內容使用繁體中文、哪些使用英文，
以及哪些是程式識別碼、任何情況下都不得因為「翻譯」而變更。

## 一、使用繁體中文

判準是「受眾」，不是檔案位置：凡是給維護者閱讀的輸出與文件，
不論實際位於哪個目錄，一律使用繁體中文。

- `scripts/` 的錯誤訊息、警告訊息、終端輸出
- GitHub Actions 產生的 issue 標題與內文（例如 `staleness.yml`
  建立的待查核條目 issue）
- 所有程式碼註解
- `schema.yml`、`vocab.yml`、`sources.yml` 的說明性註解
- `CONTRIBUTING.md`、`PROJECT_CONTEXT.md`、`DECISIONS.md`、
  `README.md`
- PR 標題與內文、commit 訊息的描述部分
- verification-notes 與終端回報

## 二、使用英文

- `tracker.yml` 中雙語欄位的 `en` 部分
- `content/articles/` 的英文版文章

## 三、不得變更（程式識別碼）

以下屬於程式識別碼，任何語言慣例都不適用，永遠維持原樣：

- YAML 欄位名稱（例如 `jurisdiction`、`applies_in`、`review_status`）
- 所有 enum 值（例如 `sdoc`、`third_party`、`pending`）
- 檔名、分支名、目錄名
- commit 訊息的 type 前綴（`feat` / `fix` / `chore` / `docs` / `refactor`）

## 四、維持英文（工具鏈慣例）

以下項目維持英文，理由是與 GitHub 生態的通用慣例一致，
英文在 CI 介面中可讀性較佳：

- GitHub Actions 的 workflow 名稱與 step 名稱
- commit 訊息的 type 前綴
- YAML 欄位名稱、enum 值
- 檔名、分支名、目錄名

## commit 訊息格式

```
feat: 新增 applies_in 欄位以支援超國家層級法規
fix: 修正 *_or_null 型別在值為 null 時誤判為缺漏
chore: 新增 .gitignore
```

type 前綴維持英文（`feat` / `fix` / `chore` / `docs` / `refactor`），
冒號後的描述文字使用繁體中文。

## PR 內文固定段落

每個 PR 內文固定包含以下四個段落：

```
## 變更摘要

## 為什麼改

## 驗證結果

## 待你確認
```

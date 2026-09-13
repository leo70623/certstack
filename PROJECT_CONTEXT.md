# CertStack — 專案背景

## 目的

CertStack 追蹤消費性電子產品跨九個法域的全球法規要求：

- EU（歐盟）
- UK（英國）
- US（美國）
- CN（中國）
- KR（南韓）
- JP（日本）
- SA（沙烏地阿拉伯）
- AE（阿拉伯聯合大公國）
- ZA（南非）

## 範疇

範疇限定於影響消費性電子產品（及其密切相關元件：電源供應器、電池、
線材/連接器、包裝、軟體/韌體）的法規——不包含一般產品安全或
不相關的產業。

## 結構

- **tracker**（`data/tracker.yml`）為主要內容類型：一份結構化、
  可機器讀取的法規條目表。
- **文章**（`content/articles/`）為次要內容：敘事性的說明與解讀，
  用以輔助 tracker，而非取代它。
- 標籤產生器工具（`tools/garan/`）協助內容標籤化。

## 真實來源

本 repository 為唯一真實來源。已發布的網站僅是渲染層——本身不具
獨立狀態，所有編輯都在本 repo 中進行。

## 資料誠信原則

- 每筆條目的 `last_verified` 與 `last_reviewed` 都必須顯示於前端。
  不得隱藏這些日期。
- `confidence: medium` 或 `confidence: low` 的條目，必須在 UI 中
  明顯標示——不得以與 `confidence: high` 條目相同的視覺權重呈現。
- 罰則欄位記錄的是**執法機制**，而非金額。多數罰則是由各國國內
  轉換立法訂定，而非法規本身，單一數字會誤導實際情況。僅
  `enforcement.penalty_range` 可包含具體數字，且僅限於法規原文
  明確指定單一固定金額的情況。
- `review_status: pending` 的條目必須在前端顯示明確指示，標示為
  「待人工複核 / Pending human review」。此為在上述 `confidence`
  標示之外「額外」必須有的標示，而非取代它。
- 前台必須對 `entry_status: stub` 的條目顯示「資料建置中 / Entry
  in progress」標示，並顯示已知的一手來源連結。stub 條目不得
  呈現為完整資料。

## 內容規範

- 法規本文可自由引用/摘錄。
- 標準文本（GB、EN、ISO 及同類標準）**不得**重製——不得複製標準
  制定機構文本中的條文、表格或限值。
- `instrument_type: mandatory_standard` 的條目僅記錄結構化欄位，
  不得為此類條目撰寫內容摘要。
- 真實法規 id 絕不可綁定尚未查證的欄位值。範本或佔位條目一律
  須使用 `example-` 前綴的 id，且 citation 須明確標示為佔位內容。
  任何尚未經人工逐字對照官方來源查核過的欄位值，都不得填入
  具有真實法規 id 的條目中。

## 語言策略

- 所有結構化的 tracker 欄位皆完全雙語（en/zh 皆為必填）。
- 長文內容（文章）採選擇性翻譯，並非預設全譯——翻譯成本高，且長文
  容易過時，而結構化欄位變動頻率低、維持雙語成本低。

## URL 結構

- `/en/reg/<id>` — 英文法規條目頁面
- `/zh/reg/<id>` — 中文法規條目頁面
- `/en/guides/<slug>` — 英文指南/文章
- `/zh/guides/<slug>` — 中文指南/文章
- 超國家層級條目（`jurisdiction: GCC` 或 `EU`）在 URL 中使用自身的
  jurisdiction（例如 `/en/reg/gcc-bd-142004-01`），不依會員國各自
  重複建立。

# HUMAN404 專案技術文件 (Technical Documentation)

**版本**：3.0 Final
**日期**：2025-12-24
**專案目標**：建置一個基於 Dify + LLM 的智能助手，能夠透過自然語言對話，自動調度 AWS 資源 (EC2/S3) 並整合 Google 搜尋資訊。

---

## 1. 系統架構 (System Architecture)

本專案由三個主要部分組成：

1.  **前端 (Client)**：`dify_cli.py` (Python CLI)
    *   提供終端機介面，接收使用者自然語言指令。
    *   透過 REST API 與 Dify Server 溝通。
    *   負責解析並美化回傳結果 (Markdown渲染、JSON 表格化)。

2.  **核心大腦 (Dify Workflow)**：`AWS_Project_Gemini3.yml`
    *   **LLM 模型**：`gemini-3-pro-preview` (或 `gemini-1.5-pro-latest`)。
    *   **參數提取 (Parameter Extractor)**：分析意圖 (`web_search`, `start_ec2` 等) 並提取參數 (Instance ID/Name)。
    *   **意圖路由 (Intent Router)**：將請求分流至 Google 搜尋或 AWS 操作路徑。
    *   **翻譯官節點 (Code Node)**：解決 Google Search 回傳 JSON 導致 LLM 無法讀取的格式問題。
    *   **LLM 摘要**：閱讀搜尋結果並撰寫人類可讀的摘要。

3.  **後端執行 (Backend)**：AWS Lambda (`aws_lambda_handler.py`)
    *   **框架**：FastAPI + Mangum + Boto3。
    *   **功能**：EC2 (List/Start/Stop)、S3 (List Buckets/Files)。
    *   **智能解析**：支援透過 Name Tag 自動查找 Instance ID。

---

## 2. 關鍵技術實作與除錯紀錄

在今天的開發過程中，我們解決了多個關鍵技術障礙：

### A. AWS Lambda 建置與除錯
*   **問題**：原始提供的 Lambda 僅回傳 Hello World，且缺乏實際功能。
*   **實作**：
    *   編寫了基於 FastAPI 的 `aws_lambda_handler.py`。
    *   實作了 `resolve_instance_id` 函式，讓使用者說「關閉 test」也能自動找到對應的 `i-xxxxx` ID。
    *   加入了嚴格的輸入驗證 (回傳 400 Bad Request)，防止 Dify 在參數錯誤時無限重試 (500 Error)。
*   **部署**：建立了 `deploy_lambda.sh` 自動化打包腳本，解決了依賴包結構錯誤與 Python 版本 (`3.12`) 不相容的問題。

### B. Dify Workflow 修復 (YAML Level)
*   **Provider ID 錯誤**：
    *   **現象**：匯入 Workflow 時報錯 `provider_id missing` 或 `UUID invalid`。
    *   **解決**：直接查詢 Postgres 資料庫 (`tool_api_providers` 表)，取得正確的 UUID (`a3f...`) 並寫入 YAML。
*   **變數傳遞失敗**：
    *   **現象**：Lambda 收到字串 `{{#param...#}}` 而非數值。
    *   **解決**：將 Tool 參數類型從 `mixed` (混合) 強制改為 `variable` (變數引用)，確保值被正確傳遞。

### C. Google Search 整合 (翻譯官模式)
*   **問題**：Serper 工具回傳 JSON 格式，但 LLM 節點無法直接讀取，導致報錯 `contents are required`。
*   **解決**：
    *   在 Search 與 LLM 之間插入一個 **Code Node (Python)**。
    *   邏輯：`Input (JSON) -> json.dumps() -> Output (String)`。
    *   這充當了「翻譯官」，將複雜的物件轉為純文字，讓 LLM 順利讀取並進行摘要。

### D. CLI 客戶端開發
*   **功能**：使用 `rich` 函式庫打造了現代化的 CLI 介面。
*   **認證**：解決了多次 API Key (`401 Unauthorized`) 問題，透過直接查詢資料庫取得最新 Token。
*   **顯示優化**：自動判斷回傳資料類型，若為 EC2 列表則顯示表格，若為文字則顯示 Markdown。

---

## 3. 檔案清單 (File Manifest)

| 檔案名稱 | 用途 | 狀態 |
| :--- | :--- | :--- |
| **`dify_cli.py`** | 使用者操作介面 (HUMAN404) | ✅ 完成 |
| **`AWS_Project_Gemini3.yml`** | Dify Workflow 定義檔 (含完整邏輯) | ✅ 完成 |
| **`aws_lambda_handler.py`** | AWS Lambda 主程式 (FastAPI) | ✅ 完成 |
| **`openapi_schema.json`** | Dify Custom Tool 定義檔 | ✅ 完成 |
| **`requirements.txt`** | Python 依賴清單 | ✅ 完成 |
| **`deploy_lambda.sh`** | Lambda 自動打包腳本 | ✅ 完成 |
| **`deployment.zip`** | 最終打包好的 Lambda 部署檔 | ✅ 完成 |

---

## 4. 維護與操作指南

### 如何更新 AWS Lambda 功能？
1.  修改 `aws_lambda_handler.py`。
2.  執行 `bash deploy_lambda.sh` 重新打包。
3.  至 AWS Console 上傳新的 `deployment.zip`。

### 如何修改對話邏輯？
1.  在 Dify Studio 匯入 `AWS_Project_Gemini3.yml`。
2.  修改後點擊 **Publish (發布)**。
3.  若新增了輸出變數，需同步更新 `dify_cli.py` 中的 `format_output` 函式。

### 如何啟動客戶端？
```bash
python3 dify_cli.py
```

#  Project : HUMAN404

> **Team HUMAN404** | 基於 Model Context Protocol (MCP) 的跨部門超級協作中樞

## 專案簡介
**HUMAN404** 是一個結合 **Dify (大腦)**、**AWS Serverless (手腳)** 與 **企業知識庫 (記憶)** 的自動化中樞。
**透過 MCP 協定，讓 AI 能夠真正執行外部搜索、內部調閱與雲端資源管理，解決企業資訊孤島與行政效率低下的問題。

## 團隊成員 (Roles)
* **P1 (Scout)**: Orson - 外部 API (Search/Email) 資源獲取、監控與驗收
* **P2 (Integrator)**: Tim - Dify 系統整合、Workflow 設計
* **P3 (PM/Infra)**: Steven - 專案統籌、地端資料庫、AWS IAM 資安
* **P4 (Builder)**: Jason - AWS Lambda 開發 (MCP Server)、API 實作
* **P5 (Soul Shaper)**: Lisa - Prompt Engineering、情境設計、QA

##  專案結構說明 (Directory Structure)
請所有成員嚴格遵守以下檔案存放位置，保持專案整潔。

| 資料夾 | 說明 | 負責人 | 備註 |
| :--- | :--- | :--- | :--- |
| `/backend` | AWS Lambda Python 原始碼 | **P4 (Jason)** | `boto3` 相關腳本放這 |
| `/docker` | 基礎設施設定檔 | **P3 (Steven)** | `docker-compose.yml`, DB config |
| `/docs` | 專案文件、Prompt 備份 | **P1, P5** | 企劃書、測試報告、System Prompts |
| `/tools` | 外部工具設定與說明 | **P1, P2** | API 串接教學、Schema 定義檔 |

##  快速啟動 (Quick Start)

### 1. 啟動 Dify (P2/P3)
```bash
cd docker
docker-compose up -d

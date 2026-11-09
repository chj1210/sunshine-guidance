# 陽光智導・廉政護航：公職人員財產申報 AI 輔助領航員 (`sunshine-guidance-and-audit-agent`)

> **監察院公職人員財產申報處｜115年公務機關AI卓越應用競賽（前瞻概念組／卓越實踐組）POC 原型系統**  
> **核心價值**：以「**良醫治未病之事前主動防呆輔導**」取代事後見獵心喜裁罰（外部公共服務有感），並以「**零幻覺確定性勾稽＋ABCX 智慧分流＋Human-in-the-Loop 雙重簽章**」減輕每年 1,398 案定期申報書審負荷（內部行政效能倍增）。

---

## 一、 系統架構與競賽加分亮點

1. **雙模式雙向賦能（Dual-Mode Empowerment）**
   - ☀️ **模式一：陽光智導艙（外部申報人＆人事／政風通報端）**  
     內建 **Stateless 無狀態隱私防火牆**（預檢草稿絕不留存供事後裁罰），針對預售屋備註欄（109訴字198號判決）、現鈔 100 萬門檻、未上市股票 vs. 事業投資分流、114/11/01 虛擬資產錢包地址新制、股票融資融券、5B 利息私人借貸、土地母子地號分割裂變、跨證券戶零股歸戶及切換頁籤遺失 `信託合約.pdf` 等 **16 條黃金準則**即時攔截並提供一鍵欄位搬移處方。
   - 🛡️ **模式二：廉政護航台（監察院第一組書審承辦端）**  
     完整搭載**李○○副院長 111～115 年真實公報申報軌跡**（淡水竹圍段配偶贈與跨表移轉鏈、泰山同興段 3 筆土地抵押權設定 **68/90 天**再信託鏈、JAGUAR 汽車滿 5 年轉註及 4 類免信託原因 RAG 合規綠章），自動預填天藍色《網路定期申報案件形式審核單 (ABCX)》、模擬 B 類紅鉛筆刪除打勾 `√`＋黃色便利貼、C 類星號 `★` 欄位轉換傳真底稿（嚴格標示「**禁止建議申報人以網路更正**」），並映射 `Y1.1`～`Y99` 共 12 種院函例稿。
2. **零幻覺純 Python 確定性計算引擎 (`backend/deterministic_rules.py`)**
   - 嚴格禁止 LLM 演算日期、股數與金額門檻！所有中華民國紀年 5 年期間、跨證券戶同檔股數歸戶（`>= 1,000` 股非零股）與名下有價證券 `>= 1,000,000` 元門檻均由純 Python 函數執行。
3. **Google ADK 五大協同 Agent ＋ Glass-box AI 治理**
   - 由總控協調官統籌四大模組子 Agent，所有對外院函與更正通知強制鎖定為 Gmail 草稿（`DRAFT_LOCKED_PENDING_HITL`），須經「**承辦人初審簽章 ➔ 組長覆核簽章**」雙重確認並寫入 SHA-256 不可竄改稽核日誌。
   - **公務同仁自主實作（零委外預算）+2 分** ＆ **地端封閉網域零外洩架構 +2 分**。

---

## 二、 專案目錄結構

```text
workspace1/
├── .agents/
│   ├── mcp_config.json                                  # MCP Server 註冊設定
│   └── skills/sunshine-guidance-and-audit-agent/
│       └── SKILL.md                                     # 16 條黃金準則與首席 AI 專家 Skill 定義
├── backend/
│   ├── main.py                                          # FastAPI 主服務與四大核心 RESTful API 端點
│   ├── adk_agents.py                                    # Google ADK 五大協同 Agent 與 HITL SHA-256 治理帳本
│   ├── deterministic_rules.py                           # 零幻覺純 Python 確定性計算函數 (a)~(d) 與 RAG 引擎
│   └── data/
│       └── seed_dual_track_poc.json                     # 雙軌測試資料集（軌A：李○○111-115公報；軌B：10大誤報攔截）
├── frontend/
│   ├── standalone_poc.html                              # 免安裝 Node.js 即開即用完整互動展示網頁（由 FastAPI / 直接託管）
│   ├── index.html / package.json / vite.config.js       # 模組化 React + Tailwind CSS + Lucide + React Flow 原始碼專案
│   └── src/
│       ├── App.jsx
│       └── components/
│           ├── SunshineGuidancePod.jsx                  # 模式一：陽光智導艙組件
│           ├── IntegrityAuditDesk.jsx                   # 模式二：廉政護航台主框架
│           ├── AssetFlowGraphTab.jsx                    # 子頁籤 A：React Flow 跨期動態資產圖譜
│           ├── RedPencilPreviewTab.jsx                  # 子頁籤 B：紅鉛筆 √ / ★ 分屏批改預覽
│           └── AbcxReviewCenterTab.jsx                  # 子頁籤 C：形式審核單 ABCX、Y1.1~Y99 院函與 HITL 簽章
├── workflow/
│   ├── agent_designer_workflow.yaml                     # Agent Designer 知識庫掛載、行事曆時效與 HITL 協同工作流
│   └── mcp_sunshine_server.py                           # JSON-RPC 2.0 MCP Server（雙軌資料集、1,398案排序與草稿鎖定）
├── tests/
│   └── test_poc_api.py                                  # Pytest 自動化單元與 API 整合測試套件
└── requirements.txt                                     # Python 相依套件清單
```

---

## 三、 快速啟動指南（免安裝 Node.js 即可完整操作展示）

本專案已貼心提供**雙模式前端交付**：除了 `frontend/src/` 下的完整模組化 React + React Flow 原始碼外，FastAPI 後端直接內建託管零編譯依賴的 `frontend/standalone_poc.html`（即使在無外網之機關封閉內網環境亦能 100% 呈現完整互動視覺與圖譜）。

### 1. 啟動 FastAPI ＋ Google ADK 後端與互動網頁
於本工作區目錄開啟 PowerShell 執行：

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

啟動後直接開啟瀏覽器造訪：
- **雙向賦能互動展示平臺首頁**：http://127.0.0.1:8000/
- **Swagger OpenAPI 互動規格文件**：http://127.0.0.1:8000/docs

### 2. 執行自動化測試驗證
```powershell
python -m pytest tests/test_poc_api.py -v
```

### 3. （選用）於具備 Node.js 環境啟動 Vite + React Flow 開發伺服器
```powershell
cd frontend
npm install
npm run dev
```

---

## 四、 核心 RESTful API 端點一覽

| HTTP 方法 | 路徑 | 功能說明 |
| :--- | :--- | :--- |
| `POST` | `/api/v1/guidance/pre-check` | 外部申報人／通報機關上傳前 16 條黃金準則體檢與溫馨處方（Stateless 無狀態隔離） |
| `POST` | `/api/v1/audit/abcx-triage` | 內部書審 ABCX 分流、紅鉛筆 `√`/`★` 標記、天藍色形式審核單預填與 `Y1.1`~`Y99` 院函 |
| `GET` | `/api/v1/audit/asset-graph/{person_id}` | 輸出跨期動態資產流向圖譜 Nodes & Edges JSON（支援 `lee-hung-chun`、`b4-land-split`） |
| `POST` | `/api/v1/governance/hitl-approve` | 記錄「承辦人 ➔ 組長」雙重人工覆核簽章與 SHA-256 Glass-box 可解釋稽核日誌 |
| `POST` | `/api/v1/rag/query` | 陽光法案、施行細則、法務部函釋與 114 書審實務指南 RAG 法源檢索問答 |

---

## 五、 參賽 3 分鐘實機 Demo 錄影腳本建議

1. **0:00 - 0:30｜破題與治理標章**：展示頂部「公務同仁自主實作 +2分標章」與點開「Mission Control: Glass-box AI 治理面板」，強調零幻覺純 Python 計算與輔導／查核無狀態防火牆。
2. **0:30 - 1:30｜模式一：☀️ 陽光智導艙（治未病防罰）**：
   - 點擊【案例1：預售屋填備註欄僅報已付290萬】➔ 紅燈攔截引用 `109訴字198號判決`，按「🛠️ 一鍵自動搬移/修正欄位」移列 `(九).1` 並改填契約總價 `2,694萬元`（免罰 45 萬）。
   - 點擊【案例4：跨證券戶零股試算】➔ 展示純 Python 自動歸戶中鋼 `800+400=1,200股` 與有價證券 `121.4萬` 之台積電 `200股` 零股強制信託明細。
3. **1:30 - 2:30｜模式二：🛡️ 廉政護航台（跨期實證與紅筆批改）**：
   - 切換【子頁籤 A】展示李○○副院長【劇本1：竹圍段配偶贈與移轉鏈】與【劇本2：同興段抵押權設定 **第68天/90天** 再信託鏈＆代理院長職稱更新】。
   - 切換【子頁籤 B】展示 B 類系統預設 `（房地總價額）` 自動紅鉛筆刪除線打勾 `√`＋黃色便利貼（移第5組），以及 C 類傳真更正底稿與紅字禁令「禁止建議申報人以網路更正」。
4. **2:30 - 3:00｜ABCX 審核單與 Human-in-the-Loop 雙簽結案**：
   - 切換【子頁籤 C】檢視 1,398 案四梯次看板、天藍色《網路定期申報案件形式審核單》、一鍵複製財管片語、預覽 `Y6` 院函草稿，最後按下「1️⃣ 承辦人簽章確認 ➔ 2️⃣ 移送組長覆核簽章」寫入 SHA-256 治理日誌收尾。

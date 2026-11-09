"""
「陽光智導・廉政護航：公職人員財產申報 AI 輔助領航員」FastAPI 後端服務主程式 (main.py)
結合 Google Agent Development Kit (ADK) 五大協同 Agent 與純 Python 確定性防幻覺計算引擎。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel, Field

from .adk_agents import (
    ADK_NATIVE_AVAILABLE,
    HITL_AUDIT_LEDGER,
    execute_abcx_triage,
    execute_guidance_precheck,
    record_hitl_approval,
    sunshine_root_coordinator,
)
from .deterministic_rules import (
    YUAN_LETTER_TEMPLATES,
    build_lee_scenario_graphs,
    check_five_year_rule,
    check_odd_lot_trust,
    load_seed_data,
    map_yuan_letter_template,
    query_rag_knowledge,
    reconcile_cross_period_assets,
)

app = FastAPI(
    title="陽光智導・廉政護航AI輔助領航員 API",
    description=(
        "監察院公職人員財產申報處 POC 後端服務（115年公務機關AI卓越應用競賽參賽原型）。"
        "整合 16 條黃金準則、五大 Google ADK 協同 Agent、零幻覺純 Python 確定性計算函數與 Human-in-the-Loop 雙重簽章治理。"
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_HTML_PATH = Path(__file__).resolve().parent.parent / "frontend" / "standalone_poc.html"


# ============================================================================
# Pydantic Request / Response Schemas
# ============================================================================
class GuidancePreCheckRequest(BaseModel):
    case_id: Optional[str] = Field(default=None, description="內建測試軌 B1~B10 或 N1 案例代碼；若留空則掃描自訂草稿欄位")
    declaration_date: str = Field(default="114/11/01", description="申報基準日（民國年）")
    remarks: Optional[str] = Field(default="", description="主表（十三）備註欄內容")
    cash_ntd: Optional[int] = Field(default=0, description="（六）現金欄申報金額")
    recent_withdrawal_ntd: Optional[int] = Field(default=0, description="基準日前夕大額提領金額")
    virtual_assets: Optional[List[Dict[str, Any]]] = Field(default=None, description="114/11/1新制虛擬資產明細")
    asset_five_year_test: Optional[Dict[str, Any]] = Field(default=None, description="單筆資產5年與房地總價額測試")
    securities_input: Optional[Dict[str, Dict[str, Any]]] = Field(default=None, description="分戶有價證券跨戶零股測試")


class AbcxTriageRequest(BaseModel):
    audit_scenario: str = Field(
        default="LEE_114_A",
        description="書審情境：LEE_114_A（李○○114定期A類） / SYSTEM_DEFAULT_B（B類紅筆打勾√） / UNREPORTED_CHANGE_C（C類星號★更正）",
    )
    violation_code: str = Field(default="Y6", description="院函例稿代碼（Y1.1 ~ Y99）")
    correction_round: int = Field(default=1, description="更正次數（1=第1次更正案<主表>、2=第2次更正案<變動表/信託表>）")
    target_form: str = Field(default="主表", description="標的申報表（主表 / 變動表 / 信託表）")


class HitlApproveRequest(BaseModel):
    case_ref: str = Field(default="A-114-1101-REGULAR", description="審核案件編號或名稱")
    abcx_result: Dict[str, str] = Field(
        default_factory=lambda: {"附表一丙": "A", "附表三": "A", "附表四": "X"},
        description="形式審核單 ABCX 判定結果",
    )
    yuan_letter_code: Optional[str] = Field(default=None, description="核定發出之 Y 系列院函例稿代碼（若無則為 None）")
    reviewer_officer: str = Field(default="第一組承辦人 李大同", description="初審簽章承辦人")
    supervisor_approver: str = Field(default="第一組組長 林○○", description="覆核簽章組長")
    decision: str = Field(default="DUAL_SIGNED_APPROVED", description="覆核決策狀態")
    note: str = Field(default="經承辦人與組長雙重人工覆核確認無誤。", description="覆核批註意見")


class RagQueryRequest(BaseModel):
    question: str = Field(..., description="申報人或承辦人之自然語言法規疑義提問")


class OddLotCalcRequest(BaseModel):
    securities_input: Dict[str, Dict[str, Any]] = Field(..., description="本人、配偶、未成年子女分戶證券明細")


class FiveYearCalcRequest(BaseModel):
    declaration_date: str = Field(default="114/11/01")
    acquisition_date: str = Field(default="109/05/19")
    reason: str = Field(default="買賣")
    price_str: str = Field(default="2,280,000")
    is_land_only: bool = Field(default=False)
    is_separate_land_building_price: bool = Field(default=False)


# ============================================================================
# 1. 四大核心 RESTful API 端點 (Competition Spec Mandatory Endpoints)
# ============================================================================
@app.post("/api/v1/guidance/pre-check", tags=["陽光智導艙 (External Guidance)"])
def api_guidance_precheck(req: GuidancePreCheckRequest) -> Dict[str, Any]:
    """提供外部申報人／通報機關上傳前 16 條黃金準則即時體檢與溫馨輔導處方（無狀態防火牆隔離）。"""
    return execute_guidance_precheck(req.model_dump(exclude_none=True))


@app.post("/api/v1/audit/abcx-triage", tags=["廉政護航台 (Internal Audit)"])
def api_audit_abcx_triage(req: AbcxTriageRequest) -> Dict[str, Any]:
    """提供內部書審承辦人 ABCX 分流、紅鉛筆 `√`/`★` 標記座標、形式審核單預填與 Y1.1~Y99 院函例稿。"""
    return execute_abcx_triage(req.model_dump())


@app.get("/api/v1/audit/asset-graph/{person_id}", tags=["廉政護航台 (Internal Audit)"])
def api_audit_asset_graph(person_id: str) -> Dict[str, Any]:
    """輸出跨期動態資產流向圖譜 Nodes & Edges JSON（支援李○○雙劇本與土地母子號分割裂變圖譜）。"""
    norm_id = person_id.strip().lower()
    if norm_id in {"lee-hung-chun", "lee", "track-a", "default"}:
        return build_lee_scenario_graphs()
    if norm_id in {"b4", "b4-land-split", "land-split"}:
        return reconcile_cross_period_assets(
            prev_records=[{"parcel": "新興段0005地號", "area_sqm": 1200.0, "owner": "張國棟"}],
            curr_records=[{"parcel": "新興段0005-1地號", "area_sqm": 600.0, "owner": "張國棟"}],
            declared_changes=[],
        )
    raise HTTPException(status_code=404, detail=f"找不到指定申報人跨期資產圖譜: {person_id}")


@app.post("/api/v1/governance/hitl-approve", tags=["Glass-box AI 治理中心"])
def api_governance_hitl_approve(req: HitlApproveRequest) -> Dict[str, Any]:
    """記錄雙重人工覆核簽章（承辦人 ➔ 組長）與不可竄改 Glass-box 可解釋日誌。"""
    return record_hitl_approval(req.model_dump())


# ============================================================================
# 2. 輔助互動端點（法規 RAG 檢索、雙軌資料集總覽、確定性試算器與前端首頁）
# ============================================================================
@app.post("/api/v1/rag/query", tags=["陽光法案 RAG 知識庫"])
def api_rag_query(req: RagQueryRequest) -> Dict[str, Any]:
    """陽光法案、施行細則、法務部函釋與 114 書審實務指南 RAG 檢索問答（強制附法源依據）。"""
    return query_rag_knowledge(req.question)


@app.post("/api/v1/deterministic/odd-lot-calc", tags=["確定性防幻覺計算引擎"])
def api_odd_lot_calc(req: OddLotCalcRequest) -> Dict[str, Any]:
    """純 Python 跨證券戶零股歸戶與 100 萬門檻確定性計算端點。"""
    return check_odd_lot_trust(req.securities_input)


@app.post("/api/v1/deterministic/five-year-calc", tags=["確定性防幻覺計算引擎"])
def api_five_year_calc(req: FiveYearCalcRequest) -> Dict[str, Any]:
    """純 Python 申報基準日滿 5 年與房地總價額紅筆打勾檢核端點。"""
    return check_five_year_rule(**req.model_dump())


@app.get("/api/v1/datasets", tags=["系統與測試集狀態"])
def api_get_datasets() -> Dict[str, Any]:
    """取得雙軌測試集摘要、Y1.1~Y99 院函例稿清單、1,398案四梯次排程與五大 ADK Agent 拓撲。"""
    seed = load_seed_data()
    return {
        "metadata": seed["metadata"],
        "adk_topology": {
            "root_agent": sunshine_root_coordinator.name,
            "adk_native_available": ADK_NATIVE_AVAILABLE,
            "sub_agents": [sa.name for sa in sunshine_root_coordinator.sub_agents],
        },
        "track_a": seed["track_a_lee_hung_chun"],
        "track_b": seed["track_b_ten_interceptions"],
        "personnel_preset": seed["personnel_notification_presets"],
        "audit_batches_114": seed["audit_batches_114"],
        "yuan_templates": YUAN_LETTER_TEMPLATES,
        "hitl_ledger": HITL_AUDIT_LEDGER,
    }


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_poc_frontend() -> Any:
    """直接託管「陽光智導・廉政護航」AI輔助領航員互動展示系統網頁原型。"""
    if FRONTEND_HTML_PATH.exists():
        return FileResponse(FRONTEND_HTML_PATH, media_type="text/html; charset=utf-8")
    return HTMLResponse("<h1>陽光智導・廉政護航 API 運行中</h1><p>請開啟 /docs 檢視 Swagger UI。</p>")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

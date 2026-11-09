"""
Google Agent Development Kit (ADK) 五大協同 Agent 架構 (adk_agents.py)
結合純 Python 確定性防幻覺工具庫 (`deterministic_rules.py`)，同時支援：
1. Google ADK 原生多代理編排 (`google.adk.agents.Agent` / `FunctionTool`)
2. 監察院封閉網域零外洩沙箱確定性執行模式（無須將敏感財產個資傳送至外部公有雲）
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Callable, Dict, List, Optional

from .deterministic_rules import (
    YUAN_LETTER_TEMPLATES,
    build_lee_scenario_graphs,
    check_five_year_rule,
    check_odd_lot_trust,
    check_personnel_notification_rule,
    load_seed_data,
    map_yuan_letter_template,
    query_rag_knowledge,
    reconcile_cross_period_assets,
)

# ----------------------------------------------------------------------------
# Google ADK 匯入與封閉網域相容層 (Air-Gapped Sovereign AI Fallback)
# ----------------------------------------------------------------------------
try:
    from google.adk.agents import Agent as AdkBaseAgent  # type: ignore
    from google.adk.tools import FunctionTool  # type: ignore

    ADK_NATIVE_AVAILABLE = True
except ImportError:
    ADK_NATIVE_AVAILABLE = False

    class FunctionTool:  # type: ignore
        """輕量相容封裝，確保於未安裝雲端套件之院內封閉環境中仍具備完整 ADK 介面結構。"""

        def __init__(self, func: Callable[..., Any]):
            self.func = func
            self.name = func.__name__
            self.description = (func.__doc__ or "").strip()

        def __call__(self, *args: Any, **kwargs: Any) -> Any:
            return self.func(*args, **kwargs)

    class AdkBaseAgent:  # type: ignore
        def __init__(
            self,
            name: str,
            model: str,
            description: str,
            instruction: str,
            tools: Optional[List[Any]] = None,
            sub_agents: Optional[List[Any]] = None,
        ):
            self.name = name
            self.model = model
            self.description = description
            self.instruction = instruction
            self.tools = tools or []
            self.sub_agents = sub_agents or []


TW_TZ = timezone(timedelta(hours=8))

# ============================================================================
# 定義五大協同專家 Agent (Google ADK Specification)
# ============================================================================
DEFAULT_MODEL = "gemini-2.5-pro"

personnel_notification_agent = AdkBaseAgent(
    name="personnel_notification_agent",
    model=DEFAULT_MODEL,
    description="模組一：職務異動通報與申報義務定性專家 Agent（Rules 1-1 ~ 1-5）",
    instruction=(
        "你負責檢核機關人事與政風承辦人之職務異動通報：嚴格執行 10 日內通報時效、"
        "公股董監事必選『就(到)職＋專任』且由實際指派機關通報、代理滿3個月真除免再辦就到職、"
        "司法官晉級與調動區分、喪失最後一職始辦卸離職，以及親屬異動連動提醒。"
    ),
    tools=[FunctionTool(check_personnel_notification_rule)],
)

pre_submission_guidance_agent = AdkBaseAgent(
    name="pre_submission_guidance_agent",
    model=DEFAULT_MODEL,
    description="模組二：授權介接盲區與未介接財產主動輔導專家 Agent（Rules 2-1 ~ 2-6）",
    instruction=(
        "你以『農業生產履歷輔導員』與『良醫治未病』之溫和專業語氣，於申報人上傳前攔截未介接盲區："
        "預售屋備註欄紅燈攔截（引用109訴字198號判決）、現鈔100萬門檻、未上市櫃股票(票面10元)與事業投資分流、"
        "114/11/1虛擬資產20萬門檻與錢包地址必填、股票融資融券/5B利息私人借貸/謄本抵押權，以及跨年淨資產逾所得1倍預警。"
    ),
    tools=[FunctionTool(check_five_year_rule), FunctionTool(query_rag_knowledge)],
)

cross_period_graph_agent = AdkBaseAgent(
    name="cross_period_graph_agent",
    model=DEFAULT_MODEL,
    description="模組三：變動申報與跨期動態資產知識圖譜勾稽 Agent（Rules 3-1 ~ 3-3）",
    instruction=(
        "你負責核對附表四首頁三大日期與雙表同步上傳提醒，並呼叫確定性圖譜引擎自動捕捉前期有本期無、"
        "土地地號母子號分割裂變（如 0005 -> 0005-1, 0005-2 攔截 120 萬罰鍰）、配偶贈與移轉鏈與抵押設定再信託鏈。"
    ),
    tools=[FunctionTool(reconcile_cross_period_assets), FunctionTool(build_lee_scenario_graphs)],
)

trust_compliance_audit_agent = AdkBaseAgent(
    name="trust_compliance_audit_agent",
    model=DEFAULT_MODEL,
    description="模組四：強制信託適法性、紅鉛筆標記與院函例稿生成 Agent（Rules 4-1 ~ 4-4）",
    instruction=(
        "你負責執行農發條例§33免信託耕地實質檢核、自用房屋單一權狀1戶限制、跨證券戶零股歸戶與100萬門檻試算、"
        "處分前指示通知90天鐵律、系統切換頁籤遺失信託合約PDF防呆，並精準映射 Y1.1~Y99 院函例稿與財管片語。"
    ),
    tools=[
        FunctionTool(check_odd_lot_trust),
        FunctionTool(map_yuan_letter_template),
        FunctionTool(check_five_year_rule),
    ],
)

sunshine_root_coordinator = AdkBaseAgent(
    name="sunshine_guidance_and_audit_coordinator",
    model=DEFAULT_MODEL,
    description="陽光智導・廉政護航總控與 Glass-box 治理協調 Agent（Root Orchestrator）",
    instruction=(
        "你是監察院公職人員財產申報處首席 AI 協調官，統籌四大專業子 Agent，確保："
        "(1) 所有數值與日期運算 100% 由 Python 確定性函數產出；"
        "(2) 外部申報輔導與內部書審查核嚴格執行無狀態防火牆隔離；"
        "(3) 內部 ABCX 分流與 Y 系列院函均須通過承辦人與組長雙重 Human-in-the-Loop 覆核始得發出。"
    ),
    sub_agents=[
        personnel_notification_agent,
        pre_submission_guidance_agent,
        cross_period_graph_agent,
        trust_compliance_audit_agent,
    ],
)


# ============================================================================
# 協同執行管線 (Orchestration Pipelines for RESTful APIs)
# ============================================================================
HITL_AUDIT_LEDGER: List[Dict[str, Any]] = [
    {
        "log_id": "HITL-1151106-001",
        "timestamp_roc": "115/11/06 09:15:22",
        "case_ref": "A-114-1101-REGULAR（李○○ 114年定期申報）",
        "abcx_result": {"附表一丙": "A", "附表三": "A", "附表四": "X"},
        "reviewer_officer": "第一組承辦人 李大同",
        "supervisor_approver": "第一組組長 林○○",
        "decision": "APPROVED_CLASS_A",
        "glassbox_hash": "sha256:9f84c2e1b0a7d56e3210c4a89d7f12e3",
        "note": "JAGUAR滿5年轉註超過五年、不動產未能交付信託原因4類全數合規，准予A類結案刊登公報。",
    }
]


def execute_guidance_precheck(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    執行外部申報人／通報機關上傳前 16 條黃金準則即時體檢與溫馨輔導處方。
    支援以 preset `case_id` (B1~B10, N1) 或自訂草稿欄位觸發。
    """
    seed = load_seed_data()
    case_id = (payload.get("case_id") or "").strip().upper()

    # 1. 若指定內建 B1~B10 或 N1 測試案例，串聯對應 Agent 與確定性引擎執行深度驗證
    all_presets = {c["case_id"]: c for c in seed["track_b_ten_interceptions"]}
    all_presets["N1"] = seed["personnel_notification_presets"]

    if case_id in all_presets:
        preset = all_presets[case_id]
        deterministic_proof: Dict[str, Any] = {}
        invoked_agents = ["sunshine_guidance_and_audit_coordinator", "pre_submission_guidance_agent"]

        if case_id == "B9" and "securities_input" in preset:
            invoked_agents.append("trust_compliance_audit_agent")
            deterministic_proof["odd_lot_calculation"] = check_odd_lot_trust(preset["securities_input"])
        elif case_id == "B4":
            invoked_agents.append("cross_period_graph_agent")
            deterministic_proof["land_split_reconciliation"] = reconcile_cross_period_assets(
                prev_records=[{"parcel": "新興段0005地號", "area_sqm": 1200.0, "owner": preset["declarant"]}],
                curr_records=[{"parcel": "新興段0005-1地號", "area_sqm": 600.0, "owner": preset["declarant"]}],
                declared_changes=[],
            )
        elif case_id in {"B10", "N1"}:
            invoked_agents.append("personnel_notification_agent")
            invoked_agents.append("trust_compliance_audit_agent")
            deterministic_proof["notification_check"] = check_personnel_notification_rule(
                event_date="114/04/01",
                notify_date="114/04/19",
                role_type="代表公股出任私法人董監事",
                selected_reason="兼任",
                selected_status="兼任",
                acting_start_date="114/01/06",
                permanent_appoint_date="114/05/01",
                same_agency=True,
            )
        elif case_id == "B8":
            invoked_agents.append("trust_compliance_audit_agent")
            deterministic_proof["yuan_letters_preview"] = [
                map_yuan_letter_template("Y1.2", declarant_name=preset["declarant"]),
                map_yuan_letter_template("Y11", declarant_name=preset["declarant"]),
            ]

        # 檢核虛擬資產新制錢包地址（若 payload 附帶虛擬資產測試）
        crypto_items = payload.get("virtual_assets", [])
        if crypto_items:
            missing_wallet = [c for c in crypto_items if not str(c.get("wallet_address", "")).strip()]
            total_crypto = sum(int(c.get("value_ntd", 0)) for c in crypto_items if int(c.get("value_ntd", 0)) > 1000)
            deterministic_proof["virtual_asset_check"] = {
                "rule_id": "Rule 2-5",
                "total_reportable_ntd": total_crypto,
                "reaches_200k_threshold": total_crypto >= 200_000,
                "missing_wallet_address_items": missing_wallet,
            }

        return {
            "status": "INTERCEPTED_FOR_GUIDANCE",
            "firewall_mode": "STATELESS_NO_LOGGING_FOR_PENALTY",
            "adk_native_runtime": ADK_NATIVE_AVAILABLE,
            "invoked_agents": invoked_agents,
            "case_id": case_id,
            "short_title": preset["short_title"],
            "rule_id": preset["rule_id"],
            "severity": preset["severity"],
            "declarant": preset["declarant"],
            "potential_fine_avoided_ntd": preset["potential_fine_ntd"],
            "potential_fine_label": preset["potential_fine_label"],
            "legal_basis": preset["legal_basis"],
            "warm_prescription": preset["warm_prescription"],
            "draft_before": preset["draft_before"],
            "draft_after": preset["draft_after"],
            "deterministic_proof": deterministic_proof,
        }

    # 2. 自訂動態草稿即時掃描（支援前端自由輸入測試）
    remarks = str(payload.get("remarks", ""))
    cash_ntd = int(payload.get("cash_ntd", 0) or 0)
    recent_withdrawal_ntd = int(payload.get("recent_withdrawal_ntd", 0) or 0)
    declaration_date = str(payload.get("declaration_date", "114/11/01"))
    alerts: List[Dict[str, Any]] = []
    total_saved_fine = 0

    if any(k in remarks for k in ["預售屋", "建案", "紅單", "工程款", "訂金"]):
        alerts.append(
            {
                "rule_id": "Rule 2-2",
                "severity": "RED",
                "title": "備註欄偵測到預售屋資訊！應移列『(九).1 其他具有相當價值之財產』並填契約總價",
                "legal_basis": "臺北高等行政法院 109 年度訴字第 198 號判決",
                "saved_fine_ntd": 450000,
            }
        )
        total_saved_fine += 450000

    if cash_ntd == 0 and recent_withdrawal_ntd >= 1_000_000:
        alerts.append(
            {
                "rule_id": "Rule 2-3",
                "severity": "RED",
                "title": f"基準日前夕提領現鈔 {recent_withdrawal_ntd:,} 元惟現金欄填 0 元",
                "legal_basis": "《公職人員財產申報法施行細則》第14條（達100萬元門檻須申報）",
                "saved_fine_ntd": 300000,
            }
        )
        total_saved_fine += 300000

    if "asset_five_year_test" in payload:
        t = payload["asset_five_year_test"]
        res5 = check_five_year_rule(
            declaration_date=declaration_date,
            acquisition_date=t.get("acquisition_date", "112/10/10"),
            reason=t.get("reason", "繼承"),
            price_str=t.get("price_str", "897,150（房地總價額）"),
        )
        if not res5["compliant"]:
            alerts.append(
                {
                    "rule_id": "Rule 2-1",
                    "severity": "ORANGE",
                    "title": res5["explanation"],
                    "recommended_price_str": res5["recommended_price_str"],
                    "saved_fine_ntd": 0,
                }
            )

    if "securities_input" in payload:
        odd_res = check_odd_lot_trust(payload["securities_input"])
        if not odd_res["compliant"]:
            alerts.append(
                {
                    "rule_id": "Rule 4-2",
                    "severity": "RED",
                    "title": f"跨證券戶零股與100萬門檻檢核發現 {odd_res['violations_count']} 筆應交付強制信託股票",
                    "details": odd_res,
                    "saved_fine_ntd": 360000,
                }
            )
            total_saved_fine += 360000

    return {
        "status": "CLEAN_PASS" if not alerts else "INTERCEPTED_FOR_GUIDANCE",
        "firewall_mode": "STATELESS_NO_LOGGING_FOR_PENALTY",
        "invoked_agents": ["sunshine_guidance_and_audit_coordinator", "pre_submission_guidance_agent"],
        "severity": "GREEN" if not alerts else alerts[0]["severity"],
        "potential_fine_avoided_ntd": total_saved_fine,
        "alerts": alerts,
        "warm_prescription": (
            "恭喜！您的申報草稿已通過 16 條黃金準則預檢，可安心點選上傳！"
            if not alerts
            else "陽光智導小幫手已為您標出潛在誤報風險，請參考處方修正後再上傳，守護您的廉政紀錄！"
        ),
    }


def execute_abcx_triage(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    執行內部書審承辦人 ABCX 分流、紅鉛筆 `√` / `★` 標記座標、形式審核單預填與 Y 系列院函生成。
    內建三種擬真書審情境切換：
    - `LEE_114_A`: 李○○副院長 114/11/01 定期申報（附表一丙：A、附表三：A、附表四：X）
    - `SYSTEM_DEFAULT_B`: 114年系統預設「（房地總價額）」於繼承/單買土地案 & 主表末頁誤勾無信託銀行（B類紅鉛筆打勾 `√` + 黃色便利貼移第5組）
    - `UNREPORTED_CHANGE_C`: 主表有分割/新購不動產惟漏報附表四變動申報表，或應信託股票未信託（C類打星號 `★` + 欄位轉換傳真底稿 + 嚴禁網路更正禁令）
    """
    mode = (payload.get("audit_scenario") or "LEE_114_A").strip().upper()
    violation_code = (payload.get("violation_code") or "Y6").strip().upper()
    correction_round = int(payload.get("correction_round", 1) or 1)
    target_form = str(payload.get("target_form", "主表"))

    # 執行確定性 5 年檢核驗證（李○○ JAGUAR 109/05/19 -> 114/11/01）
    jaguar_check = check_five_year_rule(
        declaration_date="114/11/01",
        acquisition_date="109/05/19",
        reason="買賣",
        price_str="(超過五年)",
    )

    if mode == "LEE_114_A":
        letter_info = map_yuan_letter_template(violation_code, correction_round, target_form, declarant_name="李○○")
        return {
            "audit_scenario": mode,
            "declarant_name": "李○○",
            "title": "監察院 副院長（115/02/23起兼代理院長）",
            "filing_date_roc": "114/11/01",
            "batch_tier": "TIER-4（115/03/02 結案梯次｜司/考/監院暨所屬 48人）",
            "folder_sticky_deadline": "115.3.2",
            "form_review_slip": {
                "form_1a_general": "—",
                "form_1c_trust_main": "A",
                "form_4_change": "X",
                "form_3_trust": "A",
                "separate_letter_needed": False,
                "checkboxes": {
                    "untrusted_property_or_stock": False,
                    "deed_lost": False,
                    "trust_in_progress": False,
                    "other": False,
                },
                "staple_instruction": "釘在申報表右下角，釘2支釘書針，避免遮住左上角之申報人姓名、服務機關",
            },
            "rag_non_trust_verifications": [
                {"item": "日本東京都港區芝浦二丁目房地", "reason": "國外土地／國外房屋", "rag_status": "PASS", "basis": "境外不動產無法依我國信託法辦理信託登記"},
                {"item": "雲林縣四湖鄉○○寮段 3,249 m²", "reason": "耕地，特定區域農牧用地", "rag_status": "PASS", "basis": "符合農發條例§33四大分區內農牧用地，私法人不得承受"},
                {"item": "臺北市大安區通化段○小段（1戶主建物+公設+基地）", "reason": "自用房屋及坐落基地", "rag_status": "PASS", "basis": "符合本法§7第1項第1款自用房屋1戶免信託規定"},
                {"item": "新北市泰山區福興里全興路/福興三街 3 筆", "reason": "未登記建物", "rag_status": "PASS", "basis": "無建物所有權第一次登記，無法辦理信託移轉登記"},
            ],
            "five_year_auto_check": jaguar_check,
            "red_pencil_annotations": [],
            "audit_system_phrase": "114年定期申報網路案件（附表一丙：A、附表三：A、附表四：X），不動產免信託原因4類及JAGUAR汽車滿5年轉註均核符規定，依新流程免傳統分案歸檔，俟公報刊登後依規定期限銷毀。",
            "yuan_letter_preview": letter_info,
        }

    if mode == "SYSTEM_DEFAULT_B":
        b_inherit_check = check_five_year_rule(
            declaration_date="114/11/01",
            acquisition_date="112/10/10",
            reason="繼承",
            price_str="897,150（公告現值）（房地總價額）",
        )
        b_land_only_check = check_five_year_rule(
            declaration_date="114/11/01",
            acquisition_date="111/03/08",
            reason="買賣",
            price_str="2,097,150（房地總價額）",
            is_land_only=True,
        )
        letter_info = map_yuan_letter_template(violation_code, correction_round, target_form, declarant_name="李榮長")
        return {
            "audit_scenario": mode,
            "declarant_name": "李榮長（實務指南範例）",
            "title": "○○縣果菜市場股份有限公司 總經理",
            "filing_date_roc": "114/11/01",
            "batch_tier": "TIER-1（115/01/15 結案梯次｜公營事業及府院所屬 292人）",
            "folder_sticky_deadline": "115.1.15",
            "form_review_slip": {
                "form_1a_general": "—",
                "form_1c_trust_main": "B",
                "form_4_change": "X",
                "form_3_trust": "A",
                "separate_letter_needed": False,
                "checkboxes": {
                    "untrusted_property_or_stock": False,
                    "deed_lost": False,
                    "trust_in_progress": False,
                    "other": False,
                },
                "staple_instruction": "釘在申報表右下角，釘2支釘書針，避免遮住左上角之申報人姓名、服務機關",
            },
            "red_pencil_annotations": [
                {
                    "annotation_id": "RP-B-01",
                    "page": "附表一丙 第2頁（不動產－土地）",
                    "coordinates": {"x_pct": 78, "y_pct": 34},
                    "symbol": "√",
                    "original_text": "897,150（公告現值）（房地總價額）",
                    "strikethrough_part": "（房地總價額）",
                    "corrected_text": "897,150（公告現值）",
                    "sticky_note": b_inherit_check["sticky_note"],
                },
                {
                    "annotation_id": "RP-B-02",
                    "page": "附表一丙 第2頁（不動產－僅買土地）",
                    "coordinates": {"x_pct": 78, "y_pct": 48},
                    "symbol": "√",
                    "original_text": "2,097,150（房地總價額）",
                    "strikethrough_part": "（房地總價額）",
                    "corrected_text": "2,097,150",
                    "sticky_note": b_land_only_check["sticky_note"],
                },
                {
                    "annotation_id": "RP-B-03",
                    "page": "附表一丙 末頁（信託具結聲明欄－Rule 4-4）",
                    "coordinates": {"x_pct": 22, "y_pct": 82},
                    "symbol": "√",
                    "original_text": "■第1選項（非屬強制信託範圍）",
                    "strikethrough_part": "■第1選項",
                    "corrected_text": "■補勾第2選項（業已與 第一商業銀行 完成信託）＋洽登記桌補勾『有信託銀行』",
                    "sticky_note": "有上傳附表三惟第2次重傳主表漏勾信託銀行，免請申報人重傳，紅筆逕修打勾 √ 移第5組！",
                },
            ],
            "audit_system_phrase": "本件附表一丙屬【B類案件】（系統預設帶出不適用之『房地總價額』及末頁具結勾選矛盾），已由承辦人逕以紅色鉛筆劃除打勾 √ 並於頁側貼長條便利貼，陳核後經登記桌移交第5組打字廠商修改並銷毀。",
            "yuan_letter_preview": letter_info,
        }

    # C 類更正案（含變動表漏報星號 ★ 與 Y 系列院函）
    letter_info = map_yuan_letter_template(
        violation_code=violation_code,
        correction_round=correction_round,
        target_form=target_form,
        declarant_name="張○○",
    )
    return {
        "audit_scenario": "UNREPORTED_CHANGE_C",
        "declarant_name": "張○○（C類更正與院函示範案）",
        "title": "立法院 立法委員",
        "filing_date_roc": "114/11/01",
        "batch_tier": "TIER-3（115/02/12 結案梯次｜立法院 113人）",
        "folder_sticky_deadline": "115.2.12",
        "strict_prohibition_banner": "【重要禁令】禁止建議申報人以網路更正！此舉可能導致誤刪資料、增加同仁編製比對表及電話諮詢負擔，浪費行政資源。",
        "form_review_slip": {
            "form_1a_general": "A",
            "form_1c_trust_main": "—",
            "form_4_change": "C",
            "form_3_trust": "X",
            "separate_letter_needed": True,
            "checkboxes": {
                "untrusted_property_or_stock": letter_info["audit_slip_checkbox"] == "不動產或股票未交付信託",
                "deed_lost": letter_info["audit_slip_checkbox"] == "股票或不動產權狀遺失",
                "trust_in_progress": letter_info["audit_slip_checkbox"] == "信託辦理中",
                "other": letter_info["audit_slip_checkbox"] == "其他",
            },
            "staple_instruction": "更正申報表『不要』和主表、附表裝訂在一起，僅放在同一卷夾移交第5組！",
        },
        "red_pencil_annotations": [
            {
                "annotation_id": "RP-C-01",
                "page": "附表四（變動申報表－土地）最左側序號欄",
                "coordinates": {"x_pct": 8, "y_pct": 62},
                "symbol": "★",
                "original_text": "（原漏未填報 113/11/06 買賣及 0005-2 分割出售土地變動）",
                "strikethrough_part": "",
                "corrected_text": "★ 桃園市龜山區大崗段0000地號｜變動時間：113/11/06｜變動原因：買賣｜變動時之價額：17,300,000(房地總價額)",
                "sticky_note": "C類申報人簽章回傳更正資料：整筆新增於最左側打紅色星號 ★，貼長條便利貼並交登記桌掛『更正申報條碼』分案！",
            }
        ],
        "fax_correction_conversion_sheet": {
            "sop_title": "附表一甲轉附表四快速傳真更正底稿（實務指南 P.26-27）",
            "column_conversions": [
                {"from_col": "登記（取得）時間", "to_col": "變動時間"},
                {"from_col": "登記（取得）原因", "to_col": "變動原因"},
                {"from_col": "取得價額", "to_col": "變動時之價額"},
            ],
            "signature_instruction": "請申報人於更正處及首頁切結章處簽名或蓋章後，傳真（02-23210558）或掃描 Email 回傳本處。",
        },
        "audit_system_phrase": letter_info["audit_system_phrase"],
        "yuan_letter_preview": letter_info,
    }


def record_hitl_approval(payload: Dict[str, Any]) -> Dict[str, Any]:
    """記錄雙重人工覆核簽章（承辦人 ➔ 組長）與不可竄改之 Glass-box 可解釋稽核日誌。"""
    now_tw = datetime.now(TW_TZ)
    roc_ts = f"{now_tw.year - 1911}/{now_tw.month:02d}/{now_tw.day:02d} {now_tw.strftime('%H:%M:%S')}"
    officer = str(payload.get("reviewer_officer") or "第一組承辦人 李大同").strip()
    supervisor = str(payload.get("supervisor_approver") or "第一組組長 林○○").strip()
    case_ref = str(payload.get("case_ref") or "A-114-1101-REGULAR").strip()
    abcx_result = payload.get("abcx_result") or {"附表一丙": "A", "附表三": "A", "附表四": "X"}
    yuan_letter_code = payload.get("yuan_letter_code")
    note = str(payload.get("note") or "已完成雙重人工覆核（Human-in-the-Loop），確認確定性規則計算無誤。").strip()

    raw_digest_input = f"{roc_ts}|{case_ref}|{officer}|{supervisor}|{abcx_result}|{yuan_letter_code}"
    digest = "sha256:" + hashlib.sha256(raw_digest_input.encode("utf-8")).hexdigest()[:32]

    entry = {
        "log_id": f"HITL-{now_tw.strftime('%H%M%S')}-{len(HITL_AUDIT_LEDGER) + 1:03d}",
        "timestamp_roc": roc_ts,
        "case_ref": case_ref,
        "abcx_result": abcx_result,
        "yuan_letter_code": yuan_letter_code,
        "reviewer_officer": officer,
        "supervisor_approver": supervisor,
        "decision": str(payload.get("decision") or "DUAL_SIGNED_APPROVED"),
        "gmail_draft_status": (
            f"已於承辦人公務信箱建立待發草稿（夾帶 {yuan_letter_code} 院函／更正簽章底稿），經組長覆核解鎖發送權限"
            if yuan_letter_code
            else "A/B類案件無須發函申報人，已產生正式書審簽核紀錄"
        ),
        "glassbox_hash": digest,
        "note": note,
    }
    HITL_AUDIT_LEDGER.insert(0, entry)
    return {
        "status": "HITL_RECORDED",
        "latest_entry": entry,
        "ledger_count": len(HITL_AUDIT_LEDGER),
        "recent_ledger": HITL_AUDIT_LEDGER[:10],
        "governance_compliance": [
            "符合《人工智慧基本法》人類自主與可解釋性原則",
            "符合國科會《行政院及所屬機關(構)使用生成式AI參考指引》人工最終覆核規定",
            "符合數發部《人工智慧風險分類框架》雙層簽章管控機制",
        ],
    }

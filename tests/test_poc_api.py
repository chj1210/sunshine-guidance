"""
「陽光智導・廉政護航」AI 輔助領航員自動化驗證測試套件 (test_poc_api.py)
驗證雙軌資料集、純 Python 確定性防幻覺函數、五大 ADK Agent 編排、四大核心 API 與 MCP Server。
"""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend.deterministic_rules import (
    YUAN_LETTER_TEMPLATES,
    build_lee_scenario_graphs,
    check_five_year_rule,
    check_odd_lot_trust,
    check_personnel_notification_rule,
    load_seed_data,
    map_yuan_letter_template,
    reconcile_cross_period_assets,
)
from backend.main import app
from workflow.mcp_sunshine_server import handle_jsonrpc_message

client = TestClient(app)


def test_dual_track_seed_dataset_integrity():
    seed = load_seed_data()
    # Track A: 李○○副院長 111~115 年 8 份真實公報申報紀錄
    track_a = seed["track_a_lee_hung_chun"]
    assert track_a["declarant_name"] == "李○○"
    assert track_a["spouse_name"] == "劉○○"
    assert len(track_a["filings"]) == 8

    # Track B: 10 大裁罰與誤報攔截集 (B1~B10)
    track_b = seed["track_b_ten_interceptions"]
    assert len(track_b) == 10
    assert [c["case_id"] for c in track_b] == [f"B{i}" for i in range(1, 11)]

    # 114 年度定期申報 1,398 案四梯次人數加總核驗 (292 + 181 + 113 + 812 = 1398)
    batches = seed["audit_batches_114"]
    assert batches["total_cases"] == 1398
    assert sum(b["case_count"] for b in batches["batches"]) == 1398


def test_deterministic_five_year_and_red_pencil_b_class():
    # 1. 李○○ JAGUAR 109/05/19 購入 -> 114/11/01 定期申報滿 5 年轉註（超過五年）
    res_jaguar = check_five_year_rule(
        declaration_date="114/11/01",
        acquisition_date="109/05/19",
        reason="買賣",
        price_str="（超過五年）",
    )
    assert res_jaguar["is_over_five_years"] is True
    assert res_jaguar["compliant"] is True
    assert res_jaguar["triage_class"] == "A"

    # 2. 114年系統於5年內「繼承」案件預設帶出「（房地總價額）」-> B類紅筆打勾 √ + 便利貼
    res_inherit = check_five_year_rule(
        declaration_date="114/11/01",
        acquisition_date="112/10/10",
        reason="繼承",
        price_str="897,150（公告現值）（房地總價額）",
    )
    assert res_inherit["is_over_five_years"] is False
    assert res_inherit["compliant"] is False
    assert res_inherit["triage_class"] == "B"
    assert res_inherit["red_pencil_action"]["symbol"] == "√"
    assert "第5組" in res_inherit["sticky_note"]


def test_deterministic_odd_lot_cross_account_aggregation():
    securities = {
        "本人_甲": {
            "stocks": [
                {"broker": "A戶", "ticker": "2002 中鋼", "shares": 800, "par_value": 10, "is_listed": True},
                {"broker": "B戶", "ticker": "2002 中鋼", "shares": 400, "par_value": 10, "is_listed": True},
                {"broker": "A戶", "ticker": "2330 台積電", "shares": 200, "par_value": 10, "is_listed": True},
            ],
            "bonds_ntd": 500_000,
            "funds_ntd": 700_000,
            "other_securities_ntd": 0,
        },
        "未成年子女_丙": {
            "stocks": [
                {"broker": "C戶", "ticker": "2412 中華電", "shares": 300, "par_value": 10, "is_listed": True},
            ],
            "bonds_ntd": 0,
            "funds_ntd": 100_000,
            "other_securities_ntd": 0,
        },
    }
    res = check_odd_lot_trust(securities)
    assert res["compliant"] is False
    assert res["violations_count"] == 2
    # 未成年子女丙：300股 < 1,000股 且總額 103,000 < 1,000,000 -> 免信託
    child_report = res["per_owner_summary"]["未成年子女_丙"]
    assert child_report["reaches_1m_threshold"] is False
    assert all(item["must_trust"] is False for item in child_report["tickers"])


def test_cross_period_graphs_and_68_day_mortgage_chain():
    # 1. 李○○雙劇本圖譜與 68 天精算驗證
    lee_graphs = build_lee_scenario_graphs()
    s1 = lee_graphs["scenarios"]["scenario_1"]
    s2 = lee_graphs["scenarios"]["scenario_2"]
    assert len(s1["nodes"]) == 4
    assert s2["summary_metrics"]["elapsed_days"] == 68
    assert s2["summary_metrics"]["elapsed_days"] <= s2["summary_metrics"]["statutory_limit_days"]
    assert s2["summary_metrics"]["updated_titles"] == ["1.代理院長", "2.副院長"]

    # 2. 土地 0005 -> 0005-1 / 0005-2 分割裂變漏報 C 類 ★ 攔截
    split_res = reconcile_cross_period_assets(
        prev_records=[{"parcel": "新興段0005地號", "area_sqm": 1200.0, "owner": "張國棟"}],
        curr_records=[{"parcel": "新興段0005-1地號", "area_sqm": 600.0, "owner": "張國棟"}],
        declared_changes=[],
    )
    assert split_res["compliant"] is False
    assert split_res["findings"][0]["triage_class"] == "C"
    assert split_res["findings"][0]["red_pencil_symbol"] == "★"
    assert split_res["findings"][0]["potential_fine_avoided_ntd"] == 1200000


def test_yuan_letter_12_templates_and_round_phrases():
    assert len(YUAN_LETTER_TEMPLATES) == 12
    r1 = map_yuan_letter_template("Y1.2", correction_round=1, target_form="主表", declarant_name="趙明德")
    r2 = map_yuan_letter_template("Y6", correction_round=2, target_form="變動表", declarant_name="張國棟")
    assert "【第1次】更正案<主表>" in r1["audit_system_phrase"]
    assert "【第2次】更正案<變動表>【第1次】" in r2["audit_system_phrase"]


def test_personnel_notification_rules():
    res = check_personnel_notification_rule(
        event_date="114/04/01",
        notify_date="114/04/18",
        role_type="代表公股出任私法人董監事",
        selected_reason="兼任",
        selected_status="兼任",
        acting_start_date="114/01/06",
        permanent_appoint_date="114/05/01",
        same_agency=True,
    )
    assert res["within_10_days"] is False
    assert res["delay_days"] == 17
    assert res["compliant"] is False
    assert res["acting_advice"] is not None


def test_all_fastapi_endpoints():
    # 0. Root HTML POC page
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert "陽光智導・廉政護航" in root_res.text

    # 1. POST /api/v1/guidance/pre-check (Track B1 & B9 & Custom Crypto)
    r_b1 = client.post("/api/v1/guidance/pre-check", json={"case_id": "B1"})
    assert r_b1.status_code == 200
    d_b1 = r_b1.json()
    assert d_b1["firewall_mode"] == "STATELESS_NO_LOGGING_FOR_PENALTY"
    assert d_b1["potential_fine_avoided_ntd"] == 450000

    r_b9 = client.post(
        "/api/v1/guidance/pre-check",
        json={
            "case_id": "B9",
            "virtual_assets": [{"coin": "BTC", "value_ntd": 320000, "wallet_address": ""}],
        },
    )
    assert r_b9.status_code == 200
    d_b9 = r_b9.json()
    assert "odd_lot_calculation" in d_b9["deterministic_proof"]
    assert d_b9["deterministic_proof"]["virtual_asset_check"]["reaches_200k_threshold"] is True

    # 2. POST /api/v1/audit/abcx-triage (A / B / C modes)
    for mode, expected in [("LEE_114_A", "A"), ("SYSTEM_DEFAULT_B", "B"), ("UNREPORTED_CHANGE_C", "C")]:
        r_tri = client.post(
            "/api/v1/audit/abcx-triage",
            json={"audit_scenario": mode, "violation_code": "Y6", "correction_round": 2, "target_form": "變動表"},
        )
        assert r_tri.status_code == 200
        tri_json = r_tri.json()
        if mode == "UNREPORTED_CHANGE_C":
            assert tri_json["form_review_slip"]["form_4_change"] == expected
            assert "禁止建議申報人以網路更正" in tri_json["strict_prohibition_banner"]
        else:
            assert tri_json["form_review_slip"]["form_1c_trust_main"] == expected

    # 3. GET /api/v1/audit/asset-graph/{person_id}
    r_graph = client.get("/api/v1/audit/asset-graph/lee-hung-chun")
    assert r_graph.status_code == 200
    assert r_graph.json()["scenarios"]["scenario_2"]["summary_metrics"]["elapsed_days"] == 68

    # 4. POST /api/v1/governance/hitl-approve
    r_hitl = client.post(
        "/api/v1/governance/hitl-approve",
        json={
            "case_ref": "C-114-TEST",
            "abcx_result": {"附表一甲": "A", "附表四": "C"},
            "yuan_letter_code": "Y6",
            "reviewer_officer": "第一組承辦人 測試員",
            "supervisor_approver": "第一組組長 測試組長",
        },
    )
    assert r_hitl.status_code == 200
    assert r_hitl.json()["latest_entry"]["glassbox_hash"].startswith("sha256:")

    # 5. POST /api/v1/rag/query
    r_rag = client.post("/api/v1/rag/query", json={"question": "預售屋109訴字198號判決規定怎麼報？"})
    assert r_rag.status_code == 200
    assert "198" in r_rag.json()["legal_source"]


def test_mcp_server_jsonrpc_protocol():
    init_resp = handle_jsonrpc_message({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert init_resp["result"]["serverInfo"]["name"] == "cy-sunshine-dual-track-mcp"

    rank_resp = handle_jsonrpc_message(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "rank_audit_batches_by_deadline"}}
    )
    rank_payload = json.loads(rank_resp["result"]["content"][0]["text"])
    assert rank_payload["total_cases"] == 1398
    assert rank_payload["ranked_batches"][0]["folder_sticky_label"] == "115.1.15"

    draft_resp = handle_jsonrpc_message(
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_hitl_gmail_draft",
                "arguments": {"declarant_name": "張國棟", "recipient_email": "declarant@example.gov.tw"},
            },
        }
    )
    draft_payload = json.loads(draft_resp["result"]["content"][0]["text"])
    assert draft_payload["gmail_state"] == "DRAFT_LOCKED_PENDING_HITL"
    assert draft_payload["auto_send_permitted"] is False

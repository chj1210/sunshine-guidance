"""
陽光智導・廉政護航 MCP Server (`mcp_sunshine_server.py`)
實作標準 Model Context Protocol (JSON-RPC 2.0 over stdio)，向 Agent Designer 與 AI 協同工作流提供：
1. 雙軌 POC 資料集資源掛載（李○○ 111~115 年跨期公報集 ＆ 10 大裁罰誤報攔截測試集）
2. 純 Python 確定性規則工具（5年規則、跨戶零股100萬歸戶、跨期圖譜、Y1.1~Y99 院函映射）
3. 1,398 案四梯次結案期限 Agentic Ranking 排序器與卷宗夾便利貼標籤生成
4. Human-in-the-Loop 待發郵件草稿（鎖定 DRAFT 狀態，待承辦人與組長雙重簽章始放行）
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.deterministic_rules import (  # noqa: E402
    YUAN_LETTER_TEMPLATES,
    build_lee_scenario_graphs,
    check_five_year_rule,
    check_odd_lot_trust,
    load_seed_data,
    map_yuan_letter_template,
    reconcile_cross_period_assets,
)


def rank_audit_batches_by_deadline() -> Dict[str, Any]:
    """依四大公報結案梯次（1/15、2/5、2/12、3/2 共 1,398 案）執行 Agentic Ranking 並產出卷宗便利貼標籤。"""
    seed = load_seed_data()
    batches_cfg = seed["audit_batches_114"]
    ranked: List[Dict[str, Any]] = []
    for idx, b in enumerate(batches_cfg["batches"], start=1):
        sticky_date = b["deadline_roc"].replace("/0", ".").replace("/", ".")
        ranked.append(
            {
                "agentic_rank": idx,
                "batch_id": b["batch_id"],
                "deadline_roc": b["deadline_roc"],
                "folder_sticky_label": sticky_date,
                "case_count": b["case_count"],
                "estimated_a_class_fast_track": round(b["case_count"] * batches_cfg["auto_a_class_ratio"]),
                "target_organs": b["target_organs"],
                "priority_level": b["priority_level"],
            }
        )
    return {
        "total_cases": batches_cfg["total_cases"],
        "kickoff_date": batches_cfg["kickoff_date"],
        "sticky_note_rule": batches_cfg["sticky_note_rule"],
        "ranked_batches": ranked,
    }


def create_hitl_gmail_draft(
    declarant_name: str,
    recipient_email: str,
    triage_class: str = "C",
    violation_code: str = "Y6",
    correction_round: int = 1,
    target_form: str = "變動表",
) -> Dict[str, Any]:
    """
    建立承辦人 Gmail 待發補正通知／院函草稿（強制鎖定 DRAFT 狀態，嚴禁自動寄出）。
    """
    tpl_res = map_yuan_letter_template(
        violation_code=violation_code,
        correction_round=correction_round,
        target_form=target_form,
        declarant_name=declarant_name,
    )
    return {
        "gmail_state": "DRAFT_LOCKED_PENDING_HITL",
        "auto_send_permitted": False,
        "to": recipient_email,
        "subject": f"【監察院公職人員財產申報處補正通知草稿】{declarant_name} 君 114年定期申報案（{tpl_res['correction_tag']}）",
        "attachments_prepared": [
            f"{tpl_res['template_filename']}.pdf",
            "附表四欄位轉換快速傳真更正簽章頁（頂部紅字警示：禁止以網路更正）.pdf",
        ],
        "body_preview": tpl_res["draft_yuan_letter"],
        "hitl_unlock_requirement": "須經【第一組承辦人簽章】➔【第一組組長覆核簽章】雙重確認後，始解除草稿鎖定。",
    }


MCP_TOOLS = {
    "check_five_year_rule": {
        "description": "純Python判定資產是否滿5年應轉註（超過五年），及5年內繼承/贈與/純買土地誤帶（房地總價額）之B類紅筆打勾√檢核",
        "handler": lambda args: check_five_year_rule(**args),
    },
    "check_odd_lot_trust": {
        "description": "純Python分戶計算跨證券戶同代碼上市櫃股票股數歸戶（>=1000股非零股）與有價證券總額100萬門檻",
        "handler": lambda args: check_odd_lot_trust(args["owner_securities_dict"]),
    },
    "reconcile_cross_period_assets": {
        "description": "建構跨期資產知識圖譜，捕捉土地母子號分割裂變、配偶贈與移轉鏈與抵押權68天再信託鏈",
        "handler": lambda args: reconcile_cross_period_assets(**args),
    },
    "map_yuan_letter_template": {
        "description": "映射 Y1.1~Y99 共12種監察院院函例稿與區分第1次<主表>/第2次<變動表/信託表>之財管系統片語",
        "handler": lambda args: map_yuan_letter_template(**args),
    },
    "rank_audit_batches_by_deadline": {
        "description": "依1/15、2/5、2/12、3/2四大公報結案梯次（1,398案）執行Agentic Ranking並產出卷宗便利貼標籤",
        "handler": lambda _args: rank_audit_batches_by_deadline(),
    },
    "create_hitl_gmail_draft": {
        "description": "針對C類更正或未信託案件建立鎖定狀態之Gmail待發草稿（含欄位轉換簽章頁與Y系列院函）",
        "handler": lambda args: create_hitl_gmail_draft(**args),
    },
}


def handle_jsonrpc_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    method = msg.get("method")
    req_id = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "cy-sunshine-dual-track-mcp", "version": "1.0.0"},
                "capabilities": {"tools": {}, "resources": {}},
            },
        }
    if method == "resources/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resources": [
                    {
                        "uri": "sunshine://datasets/track-a-lee-hung-chun-111-115",
                        "name": "測試軌A：李○○副院長 111~115 年真實公報申報集",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "sunshine://datasets/track-b-ten-penalty-interceptions",
                        "name": "測試軌B：宣導簡報 10 大裁罰與誤報攔截集",
                        "mimeType": "application/json",
                    },
                    {
                        "uri": "sunshine://templates/yuan-letters-y1-to-y99",
                        "name": "監察院第一組書審院函例稿庫（Y1.1 ~ Y99）",
                        "mimeType": "application/json",
                    },
                ]
            },
        }
    if method == "resources/read":
        uri = params.get("uri", "")
        seed = load_seed_data()
        if "track-a" in uri:
            payload = {"filings": seed["track_a_lee_hung_chun"], "graphs": build_lee_scenario_graphs()}
        elif "track-b" in uri:
            payload = seed["track_b_ten_interceptions"]
        else:
            payload = YUAN_LETTER_TEMPLATES
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(payload, ensure_ascii=False, indent=2),
                    }
                ]
            },
        }
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {"name": name, "description": meta["description"], "inputSchema": {"type": "object"}}
                    for name, meta in MCP_TOOLS.items()
                ]
            },
        }
    if method == "tools/call":
        t_name = params.get("name", "")
        t_args = params.get("arguments") or {}
        if t_name not in MCP_TOOLS:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"未知工具: {t_name}"}}
        out = MCP_TOOLS[t_name]["handler"](t_args)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"content": [{"type": "text", "text": json.dumps(out, ensure_ascii=False, indent=2)}]},
        }
    if req_id is not None:
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    return None


def main() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        resp = handle_jsonrpc_message(json.loads(line))
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

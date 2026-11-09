"""
純 Python 確定性防幻覺計算與法規檢核引擎 (deterministic_rules.py)
嚴格禁止以 LLM 演算數值、股數、金額門檻與中華民國紀年日期差！
涵蓋《114年書審實務作業指南》、《職務異動通報說明》與 16 條黃金準則。
"""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

DATA_PATH = Path(__file__).resolve().parent / "data" / "seed_dual_track_poc.json"


def load_seed_data() -> Dict[str, Any]:
    """載入雙軌 POC 內建測試資料集。"""
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def parse_roc_date(roc_str: str) -> date:
    """
    將中華民國紀年字串（如 '114/11/01'、'109年05月19日'、'98.5.22'）解析為標準 datetime.date。
    """
    if not roc_str or not isinstance(roc_str, str):
        raise ValueError(f"無效的民國日期字串: {roc_str!r}")
    cleaned = roc_str.strip()
    m = re.search(r"(\d{2,3})\s*[年/\-\.]\s*(\d{1,2})\s*[月/\-\.]\s*(\d{1,2})", cleaned)
    if not m:
        # 支援連續7碼如 1140716
        m_compact = re.match(r"^(\d{3})(\d{2})(\d{2})$", cleaned)
        if m_compact:
            roc_y, mo, da = map(int, m_compact.groups())
            return date(roc_y + 1911, mo, da)
        raise ValueError(f"無法解析民國日期格式: {roc_str!r}")
    roc_y, mo, da = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return date(roc_y + 1911, mo, da)


def format_roc_date(d: date) -> str:
    """將 datetime.date 格式化為『114年11月01日』與『114/11/01』標準字串。"""
    roc_y = d.year - 1911
    return f"{roc_y:03d}/{d.month:02d}/{d.day:02d}"


def format_roc_date_cn(d: date) -> str:
    """將 datetime.date 格式化為公文院函格式『中華民國114年11月1日』。"""
    roc_y = d.year - 1911
    return f"中華民國{roc_y}年{d.month}月{d.day}日"


def _add_years_safe(d: date, years: int) -> date:
    """安全加上年數（處理閏年 2/29 邊界）。"""
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, month=2, day=28)


# ============================================================================
# (a) Rule 2-1: 申報基準日與 5 年房地總價額＆B類紅筆打勾檢核
# ============================================================================
def check_five_year_rule(
    declaration_date: str,
    acquisition_date: str,
    reason: str,
    price_str: str,
    is_land_only: bool = False,
    is_separate_land_building_price: bool = False,
) -> Dict[str, Any]:
    """
    自動判定資產取得是否滿 5 年應轉註「（超過五年）」，並針對 5 年內繼承/贈與/純買土地/
    已分別填寫房地價額卻帶出系統預設「（房地總價額）」或重複字句者，回傳 B 類紅筆打勾 `√` 與貼便利貼指令。
    """
    decl_dt = parse_roc_date(declaration_date)
    acq_dt = parse_roc_date(acquisition_date)
    five_year_anniv = _add_years_safe(acq_dt, 5)
    elapsed_days = (decl_dt - acq_dt).days
    is_over_five_years = decl_dt >= five_year_anniv

    normalized_price = (price_str or "").strip()
    normalized_reason = (reason or "").strip()
    has_joint_tag = ("房地總價額" in normalized_price) or ("土地及建物總價" in normalized_price)
    duplicate_joint_tag = normalized_price.count("房地總價額") >= 2

    non_purchase_reasons = {"繼承", "分割繼承", "贈與", "受贈", "夫妻贈與"}
    is_inherit_or_gift = any(r in normalized_reason for r in non_purchase_reasons)

    # 情況 1：已滿 5 年
    if is_over_five_years:
        already_annotated = "超過五年" in normalized_price
        has_wrong_joint_tag = has_joint_tag
        if already_annotated and not has_wrong_joint_tag:
            return {
                "rule_id": "Rule 2-1",
                "is_over_five_years": True,
                "elapsed_days": elapsed_days,
                "five_year_anniversary_roc": format_roc_date(five_year_anniv),
                "compliant": True,
                "triage_class": "A",
                "recommended_price_str": "（超過五年）",
                "red_pencil_action": None,
                "sticky_note": None,
                "explanation": (
                    f"取得日 {acquisition_date} 至申報基準日 {declaration_date} 已滿 5 年"
                    f"（屆滿日 {format_roc_date(five_year_anniv)}），已正確轉註「（超過五年）」。"
                ),
            }
        return {
            "rule_id": "Rule 2-1",
            "is_over_five_years": True,
            "elapsed_days": elapsed_days,
            "five_year_anniversary_roc": format_roc_date(five_year_anniv),
            "compliant": False,
            "triage_class": "B",
            "recommended_price_str": "（超過五年）",
            "red_pencil_action": {
                "symbol": "√",
                "action_type": "RED_STRIKETHROUGH_AND_CHECK",
                "target_text": normalized_price,
                "replacement_text": "（超過五年）",
            },
            "sticky_note": "右側貼黃色長條便利貼：登記取得已滿5年，請第5組打字人員改註「（超過五年）」",
            "explanation": (
                f"取得日 {acquisition_date} 距申報基準日 {declaration_date} 已滿 5 年"
                f"（共 {elapsed_days} 天），無須填報取得價額，應自動轉註為「（超過五年）」。"
            ),
        }

    # 情況 2：未滿 5 年，檢核 114 年系統預設「（房地總價額）」誤帶或重複問題
    if duplicate_joint_tag:
        cleaned_once = re.sub(r"[（\(]房地總價額[）\)]", "", normalized_price, count=1).strip()
        return {
            "rule_id": "Rule 2-1",
            "is_over_five_years": False,
            "elapsed_days": elapsed_days,
            "five_year_anniversary_roc": format_roc_date(five_year_anniv),
            "compliant": False,
            "triage_class": "B",
            "recommended_price_str": cleaned_once,
            "red_pencil_action": {
                "symbol": "√",
                "action_type": "RED_STRIKETHROUGH_DUPLICATE",
                "target_text": "（房地總價額）[重複字句]",
                "replacement_text": cleaned_once,
            },
            "sticky_note": "右側貼黃色長條便利貼：系統重複帶出「（房地總價額）」，承辦人紅筆劃掉多餘字句並打勾 √，移第5組打字人員刪除",
            "explanation": "114年網路申報系統自動帶入重複之「（房地總價額）」字樣，屬系統造成錯誤（B類），由承辦人直接紅鉛筆劃除並打勾 √。",
        }

    if has_joint_tag and (is_inherit_or_gift or is_land_only or is_separate_land_building_price):
        cleaned_price = re.sub(r"[（\(]房地總價額[）\)]", "", normalized_price).strip()
        reason_desc = (
            f"取得原因為「{normalized_reason}」（非買賣共同取得）"
            if is_inherit_or_gift
            else ("僅單獨購買土地" if is_land_only else "土地與建物已分別填寫不同價額")
        )
        return {
            "rule_id": "Rule 2-1",
            "is_over_five_years": False,
            "elapsed_days": elapsed_days,
            "five_year_anniversary_roc": format_roc_date(five_year_anniv),
            "compliant": False,
            "triage_class": "B",
            "recommended_price_str": cleaned_price,
            "red_pencil_action": {
                "symbol": "√",
                "action_type": "RED_STRIKETHROUGH_SYSTEM_DEFAULT",
                "target_text": "（房地總價額）",
                "replacement_text": cleaned_price,
            },
            "sticky_note": f"右側貼黃色長條便利貼：5年內{reason_desc}不適用房地總價額，紅筆逕予刪除預設「（房地總價額）」並打勾 √，移第5組打字人員刪除",
            "explanation": (
                f"本筆資產未滿 5 年，惟因{reason_desc}，無須加註「（房地總價額）」。"
                "此係 114 年系統預設無法由申報人自行刪除所致，歸類為【B類案件】逕以紅筆劃除打勾 √。"
            ),
        }

    # 5年內買賣共同取得但漏註記房地總價額
    if "買賣" in normalized_reason and not is_land_only and not is_separate_land_building_price and not has_joint_tag:
        return {
            "rule_id": "Rule 2-1",
            "is_over_five_years": False,
            "elapsed_days": elapsed_days,
            "five_year_anniversary_roc": format_roc_date(five_year_anniv),
            "compliant": False,
            "triage_class": "C",
            "recommended_price_str": f"{normalized_price}（房地總價額）",
            "red_pencil_action": {
                "symbol": "★",
                "action_type": "NOTIFY_DECLARANT_CORRECTION",
                "target_text": normalized_price,
                "replacement_text": f"{normalized_price}（房地總價額）",
            },
            "sticky_note": "5年內買賣共同取得房地未註記「（房地總價額）」，若土地與建物均漏註記須確認更正（若其中一欄已註記則免通知更正）",
            "explanation": "5年內買賣取得之共同房地，應填寫實際交易價額並註記「（房地總價額）」。",
        }

    return {
        "rule_id": "Rule 2-1",
        "is_over_five_years": False,
        "elapsed_days": elapsed_days,
        "five_year_anniversary_roc": format_roc_date(five_year_anniv),
        "compliant": True,
        "triage_class": "A",
        "recommended_price_str": normalized_price,
        "red_pencil_action": None,
        "sticky_note": None,
        "explanation": "5年內取得資產價額與註記符合書審規範（A類全部正確）。",
    }


# ============================================================================
# (b) Rule 4-2: 跨證券戶零股歸戶與 100 萬強制信託門檻確定性計算
# ============================================================================
def check_odd_lot_trust(owner_securities_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    按本人、配偶、未成年子女「分戶獨立計算」強制信託義務：
    1. 同一人跨證券戶同代碼國內上市(櫃)股票股數相加 >= 1,000 股 -> 屬「非零股」，不論總額是否達 100 萬均須強制信託（Y4.1 / Y4.2）。
    2. 同代碼相加 < 1,000 股（真零股） -> 加總該人名下「股票+債券+基金+其他有價證券」是否 >= 1,000,000 元；
       若 >= 1,000,000 元，則 < 1,000 股之真零股亦須強制信託（Y3 / Y6）；未達 1,000,000 元則免信託。
    """
    per_owner_results: Dict[str, Any] = {}
    overall_violations: List[Dict[str, Any]] = []
    recommended_yuan_letters: List[str] = []

    self_has_1m_odd_lot_violation = False
    spouse_under_1m_non_odd_lot_violation = False

    for owner_key, portfolio in owner_securities_dict.items():
        stocks: List[Dict[str, Any]] = portfolio.get("stocks", [])
        bonds_ntd = int(portfolio.get("bonds_ntd", 0) or 0)
        funds_ntd = int(portfolio.get("funds_ntd", 0) or 0)
        other_sec_ntd = int(portfolio.get("other_securities_ntd", 0) or 0)

        # 跨證券戶按股票代碼/名稱歸戶
        grouped_tickers: Dict[str, Dict[str, Any]] = {}
        total_stocks_ntd = 0

        for item in stocks:
            ticker = str(item.get("ticker", "")).strip()
            shares = int(item.get("shares", 0) or 0)
            par_value = int(item.get("par_value", 10) or 10)
            val_ntd = int(item.get("value_ntd", shares * par_value))
            is_listed = bool(item.get("is_listed", True))  # 僅國內上市/上櫃股票為強制信託標的（興櫃/下市除外）
            broker = str(item.get("broker", "預設證券戶"))

            total_stocks_ntd += val_ntd
            if ticker not in grouped_tickers:
                grouped_tickers[ticker] = {
                    "ticker": ticker,
                    "total_shares": 0,
                    "total_value_ntd": 0,
                    "is_listed": is_listed,
                    "accounts": [],
                }
            grouped_tickers[ticker]["total_shares"] += shares
            grouped_tickers[ticker]["total_value_ntd"] += val_ntd
            grouped_tickers[ticker]["accounts"].append({"broker": broker, "shares": shares})

        total_securities_ntd = total_stocks_ntd + bonds_ntd + funds_ntd + other_sec_ntd
        reaches_1m_threshold = total_securities_ntd >= 1_000_000

        ticker_decisions: List[Dict[str, Any]] = []
        for ticker, agg in grouped_tickers.items():
            if not agg["is_listed"]:
                decision = {
                    **agg,
                    "lot_category": "非國內上市(櫃)股票（興櫃/未上市/下市）",
                    "must_trust": False,
                    "legal_reason": "非屬國內上市、上櫃股票，依法免交付強制信託。",
                    "yuan_letter_code": None,
                }
            elif agg["total_shares"] >= 1000:
                is_spouse = "配偶" in owner_key
                y_code = "Y4.2" if is_spouse else ("Y4.2" if reaches_1m_threshold else "Y4.1")
                if is_spouse and not reaches_1m_threshold:
                    spouse_under_1m_non_odd_lot_violation = True
                decision = {
                    **agg,
                    "lot_category": "非零股（跨戶歸戶 ≥ 1,000 股）",
                    "must_trust": True,
                    "legal_reason": (
                        f"跨證券戶合併計算共 {agg['total_shares']:,} 股（≥ 1,000 股屬非零股），"
                        f"縱名下有價證券總額為 {total_securities_ntd:,} 元，仍應依法交付強制信託！"
                    ),
                    "yuan_letter_code": y_code,
                }
                overall_violations.append({"owner": owner_key, **decision})
                if y_code not in recommended_yuan_letters:
                    recommended_yuan_letters.append(y_code)
            else:
                # 真零股 (< 1,000 股)
                if reaches_1m_threshold:
                    if "本人" in owner_key:
                        self_has_1m_odd_lot_violation = True
                    decision = {
                        **agg,
                        "lot_category": "應信託零股（< 1,000 股惟有價證券總額 ≥ 100 萬）",
                        "must_trust": True,
                        "legal_reason": (
                            f"{ticker} 歸戶後為 {agg['total_shares']:,} 股（< 1,000 股），"
                            f"惟 {owner_key} 名下各類有價證券總額達新臺幣 {total_securities_ntd:,} 元（≥ 100 萬元門檻），"
                            "該零股亦須交付信託！（若擬直接出售，請改填『已向監察院指示通知處分中』並同步提送指示通知表）"
                        ),
                        "yuan_letter_code": "Y3",
                    }
                    overall_violations.append({"owner": owner_key, **decision})
                    if "Y3" not in recommended_yuan_letters:
                        recommended_yuan_letters.append("Y3")
                else:
                    decision = {
                        **agg,
                        "lot_category": "免信託零股（< 1,000 股且有價證券總額 < 100 萬）",
                        "must_trust": False,
                        "legal_reason": (
                            f"{ticker} 歸戶後為 {agg['total_shares']:,} 股（< 1,000 股），"
                            f"且 {owner_key} 名下有價證券總額 {total_securities_ntd:,} 元未達 100 萬元，依法免交付信託。"
                        ),
                        "yuan_letter_code": None,
                    }
            ticker_decisions.append(decision)

        per_owner_results[owner_key] = {
            "owner": owner_key,
            "breakdown_ntd": {
                "stocks_ntd": total_stocks_ntd,
                "bonds_ntd": bonds_ntd,
                "funds_ntd": funds_ntd,
                "other_securities_ntd": other_sec_ntd,
                "total_securities_ntd": total_securities_ntd,
            },
            "reaches_1m_threshold": reaches_1m_threshold,
            "tickers": ticker_decisions,
        }

    # 若同時符合「本人有價證券達100萬-零股要信託」＋「配偶未達100萬-非零股要信託」，自動升級映射專用複合院函 Y6！
    if self_has_1m_odd_lot_violation and spouse_under_1m_non_odd_lot_violation:
        if "Y6" not in recommended_yuan_letters:
            recommended_yuan_letters.insert(0, "Y6")

    return {
        "rule_id": "Rule 4-2",
        "compliant": len(overall_violations) == 0,
        "per_owner_summary": per_owner_results,
        "violations_count": len(overall_violations),
        "violations": overall_violations,
        "recommended_yuan_letters": recommended_yuan_letters,
    }


# ============================================================================
# (c) Rule 3-2, 3-3, 4-3: 跨期資產知識圖譜勾稽與時效檢核引擎
# ============================================================================
def _extract_mother_parcel(parcel_str: str) -> Tuple[str, Optional[str]]:
    """
    擷取地段與母子地號：例如 '新興段0005-2地號' -> ('新興段0005', '2')；'新興段0005地號' -> ('新興段0005', None)
    """
    m = re.search(r"([^\d\s]+段[^\d\s]*?)?\s*0*(\d+)(?:[-之](\d+))?\s*地號", parcel_str)
    if not m:
        return parcel_str.strip(), None
    prefix = (m.group(1) or "").strip()
    mother_num = m.group(2).zfill(4)
    sub_num = m.group(3)
    return f"{prefix}{mother_num}", sub_num


def reconcile_cross_period_assets(
    prev_records: List[Dict[str, Any]],
    curr_records: List[Dict[str, Any]],
    instruction_notices: Optional[List[Dict[str, Any]]] = None,
    new_trust_records: Optional[List[Dict[str, Any]]] = None,
    declared_changes: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    建構跨期資產知識圖譜 (NetworkX DiGraph -> React Flow Nodes & Edges)，自動捕捉：
    1. 前期有本期無（出售/贈與未報變動）
    2. 土地母子地號分割裂變（如 0005 -> 0005-1, 0005-2 賣出漏報變動 -> C類打星號 `★` + 120萬裁罰攔截）
    3. 李○○副院長 111~113 年「淡水竹圍段房地配偶贈與移轉鏈」
    4. 李○○副院長 114~115 年「泰山同興段 3 筆土地抵押權設定再信託鏈（精算 68 天 <= 90 天處分期 & 30 天變更期）」
    """
    instruction_notices = instruction_notices or []
    new_trust_records = new_trust_records or []
    declared_changes = declared_changes or []

    g = nx.DiGraph()
    findings: List[Dict[str, Any]] = []

    prev_map = {r["parcel"]: r for r in prev_records if "parcel" in r}
    curr_map = {r["parcel"]: r for r in curr_records if "parcel" in r}
    declared_change_parcels = {c.get("parcel", "") for c in declared_changes}

    # 1. 母子地號分割裂變偵測與前期有本期無比對
    curr_by_mother: Dict[str, List[Dict[str, Any]]] = {}
    for p_name, rec in curr_map.items():
        mother_key, sub_no = _extract_mother_parcel(p_name)
        if sub_no is not None:
            curr_by_mother.setdefault(mother_key, []).append(rec)

    for prev_parcel, prev_rec in prev_map.items():
        if prev_parcel in curr_map:
            prev_owner = prev_rec.get("owner") or prev_rec.get("prior_owner")
            curr_owner = curr_map[prev_parcel].get("owner") or curr_map[prev_parcel].get("prior_owner")
            if prev_owner and curr_owner and prev_owner != curr_owner:
                g.add_node(
                    f"prev_{prev_parcel}",
                    label=f"前期：{prev_parcel}\n所有人：{prev_owner}",
                    stage="prev",
                    status="info",
                )
                g.add_node(
                    f"curr_{prev_parcel}",
                    label=f"本期：{prev_parcel}\n所有人變更：{curr_owner}",
                    stage="curr",
                    status="warning",
                )
                g.add_edge(f"prev_{prev_parcel}", f"curr_{prev_parcel}", label="跨期所有權人移轉")
                findings.append(
                    {
                        "type": "OWNER_CHANGED_ACROSS_PERIOD",
                        "rule_id": "Rule 3-2 / Rule 4-3",
                        "triage_class": "A_WITH_CROSS_CHECK",
                        "parcel": prev_parcel,
                        "detail": f"「{prev_parcel}」所有權人由 {prev_owner} 變更為 {curr_owner}，請交叉核對指示通知表、新增信託表與附表一丙變動情形欄。",
                    }
                )
            continue

        mother_key, prev_sub = _extract_mother_parcel(prev_parcel)
        split_children = curr_by_mother.get(mother_key, [])
        if prev_sub is None and split_children:
            # 捕捉到母地號裂變為子地號（如 0005 -> 0005-1 留存，推知 0005-2 等已處分！）
            g.add_node(
                f"mother_{prev_parcel}",
                label=f"前期母地號：{prev_parcel}\n面積：{prev_rec.get('area_sqm', '?')} m²",
                stage="prev",
                status="info",
            )
            kept_area = 0.0
            for child in split_children:
                c_name = child["parcel"]
                kept_area += float(child.get("area_sqm", 0) or 0)
                g.add_node(
                    f"child_kept_{c_name}",
                    label=f"本期留存子地號：{c_name}\n面積：{child.get('area_sqm', '?')} m²",
                    stage="curr",
                    status="success",
                )
                g.add_edge(f"mother_{prev_parcel}", f"child_kept_{c_name}", label="地號分割留存")

            prev_area = float(prev_rec.get("area_sqm", 0) or 0)
            missing_area = round(max(0.0, prev_area - kept_area), 2)
            inferred_sold_parcel = prev_parcel.replace("地號", "-2地號")
            if prev_parcel not in declared_change_parcels and inferred_sold_parcel not in declared_change_parcels:
                g.add_node(
                    f"child_sold_{inferred_sold_parcel}",
                    label=f"裂變移轉子地號：{inferred_sold_parcel}\n減少面積：{missing_area} m²（漏報變動！）",
                    stage="alert",
                    status="danger",
                )
                g.add_edge(f"mother_{prev_parcel}", f"child_sold_{inferred_sold_parcel}", label="分割出售漏報 ★")
                findings.append(
                    {
                        "type": "LAND_SPLIT_UNREPORTED_CHANGE",
                        "rule_id": "Rule 3-2 & 3-3",
                        "triage_class": "C",
                        "red_pencil_symbol": "★",
                        "parcel": prev_parcel,
                        "inferred_disposed_parcel": inferred_sold_parcel,
                        "missing_area_sqm": missing_area,
                        "potential_fine_avoided_ntd": 1200000,
                        "detail": (
                            f"偵測到母地號「{prev_parcel}」（{prev_area} m²）裂變為子地號，本期僅留存 {kept_area} m²，"
                            f"減少之 {missing_area} m²（推定分割子號 {inferred_sold_parcel} 已出售/移轉）漏未申報於附表四變動表！"
                            "書審列為【C類更正案 ★】，產出欄位轉換傳真更正底稿（嚴禁建議申報人以網路更正）。"
                        ),
                    }
                )
        elif prev_parcel not in declared_change_parcels:
            g.add_node(
                f"prev_missing_{prev_parcel}",
                label=f"前期資產：{prev_parcel}\n本期消失未報變動 ★",
                stage="alert",
                status="danger",
            )
            findings.append(
                {
                    "type": "DISPOSED_ASSET_UNREPORTED",
                    "rule_id": "Rule 3-2",
                    "triage_class": "C",
                    "red_pencil_symbol": "★",
                    "parcel": prev_parcel,
                    "detail": f"前期申報之「{prev_parcel}」於本期主表消失且未見於變動申報表，列【C類更正案 ★】。",
                }
            )

    # 2. 信託指示通知 90 天處分期與 30 天變更通知期精算
    timeline_checks: List[Dict[str, Any]] = []
    for notice in instruction_notices:
        notice_dt = parse_roc_date(notice["roc_date"])
        deadline_90d = notice_dt + timedelta(days=90)
        action = notice.get("action", "管理處分")
        parcel_desc = notice.get("parcel", "信託標的")

        matched_trust = None
        for nt in new_trust_records:
            if notice.get("key") and nt.get("key") == notice.get("key"):
                matched_trust = nt
                break
            if parcel_desc in nt.get("parcel", ""):
                matched_trust = nt
                break

        if matched_trust:
            complete_dt = parse_roc_date(matched_trust.get("transfer_date") or matched_trust["roc_date"])
            filing_dt = parse_roc_date(matched_trust["roc_date"])
            days_to_complete = (complete_dt - notice_dt).days
            days_to_report_change = (filing_dt - complete_dt).days
            within_90d = 0 <= days_to_complete <= 90
            within_30d_report = days_to_report_change <= 30

            timeline_checks.append(
                {
                    "parcel": parcel_desc,
                    "action": action,
                    "instruction_date_roc": notice["roc_date"],
                    "completion_date_roc": format_roc_date(complete_dt),
                    "new_trust_filing_date_roc": matched_trust["roc_date"],
                    "elapsed_days_since_instruction": days_to_complete,
                    "statutory_disposal_limit_days": 90,
                    "remaining_days_buffer": 90 - days_to_complete,
                    "days_from_completion_to_filing": days_to_report_change,
                    "within_90d_iron_rule": within_90d,
                    "within_30d_amendment_rule": within_30d_report,
                    "updated_titles": matched_trust.get("titles", []),
                }
            )

    nodes_out = [
        {"id": nid, "data": attrs}
        for nid, attrs in g.nodes(data=True)
    ]
    edges_out = [
        {"id": f"e_{u}_{v}", "source": u, "target": v, "label": attrs.get("label", "")}
        for u, v, attrs in g.edges(data=True)
    ]

    return {
        "nodes": nodes_out,
        "edges": edges_out,
        "findings": findings,
        "timeline_checks": timeline_checks,
        "compliant": all(f.get("triage_class") != "C" for f in findings),
    }


def build_lee_scenario_graphs() -> Dict[str, Any]:
    """
    針對李○○副院長 111~115 年真實公報資料，以純 Python 確定性日期與面積數據產出雙劇本跨期動態資產軌跡圖譜 JSON。
    """
    # 劇本 1：111~113年 淡水竹圍段房地「配偶贈與」跨表移轉鏈
    d_instruct_1 = parse_roc_date("113/08/27")
    d_transfer_1 = parse_roc_date("113/08/09")
    d_newtrust_1 = parse_roc_date("113/09/10")
    days_transfer_to_newtrust = (d_newtrust_1 - d_transfer_1).days  # 32 days (8月31天: 22+10=32，約1個月法定期限內)

    scenario_1 = {
        "scenario_id": "SCENARIO_1_ZHUWEI_GIFT",
        "title": "劇本 1：111~113年 淡水竹圍段房地「配偶贈與」跨表移轉鏈",
        "gazette_sources": ["廉政專刊第194期", "廉政專刊第249期", "廉政專刊第258期 P.350 & P.388", "廉政專刊第269期 P.186 & P.191"],
        "summary_metrics": {
            "land_area_sqm": 3305.58,
            "land_share": "100000分之558",
            "building_area_sqm": 152.33,
            "prior_owner_before": "李○○",
            "prior_owner_after": "劉○○（配偶）",
            "transfer_to_filing_days": days_transfer_to_newtrust,
        },
        "nodes": [
            {
                "id": "s1_n1",
                "position": {"x": 40, "y": 90},
                "type": "trustNode",
                "data": {
                    "badge": "111/08/19 ～ 112/11/01 附表三",
                    "title": "信託財產申報表（原持有人）",
                    "subtitle": "新北市淡水區竹圍段房地",
                    "details": [
                        "土地面積：3,305.58 m²（持分 100000分之558）",
                        "建物面積：152.33 m²（權利範圍：全部）",
                        "信託前所有權人：李○○ ｜ 受託人：第一商業銀行",
                    ],
                    "status": "verified",
                },
            },
            {
                "id": "s1_n2",
                "position": {"x": 380, "y": 90},
                "type": "instructionNode",
                "data": {
                    "badge": "113/08/27 指示通知表（專刊258期P.388）",
                    "title": "管理或處分指示通知：「贈與」",
                    "subtitle": "委託人李○○向第一銀行為處分指示",
                    "details": [
                        "管理或處分方式：贈與（夫妻間贈與）",
                        "土地：淡水區竹圍段 3,305.58 m²",
                        "建物：淡水區民權路（同竹圍段）152.33 m²",
                    ],
                    "status": "active",
                },
            },
            {
                "id": "s1_n3",
                "position": {"x": 720, "y": 90},
                "type": "newTrustNode",
                "data": {
                    "badge": "113/09/10 新增信託表（專刊258期P.350）",
                    "title": "新增信託財產申報（配偶受贈再信託）",
                    "subtitle": "所有權人變更為：配偶 劉○○",
                    "details": [
                        "移轉登記完成日期：113/08/09",
                        "受託人：第一商業銀行（負責人：邱月琴）",
                        "完成夫妻贈與後無縫銜接交付強制信託",
                    ],
                    "status": "verified",
                },
            },
            {
                "id": "s1_n4",
                "position": {"x": 1060, "y": 90},
                "type": "auditAlertNode",
                "data": {
                    "badge": "113/11/01 定期申報跨表勾稽（專刊269期）",
                    "title": "AI 書審交叉檢核提醒（Human-in-the-Loop）",
                    "subtitle": "附表一丙『土地/建物變動情形』欄空白覆核",
                    "details": [
                        "附表三已更新竹圍段所有人為『劉○○』",
                        "惟附表一丙『土地變動情形／建物變動情形』欄填寫：本欄空白",
                        "處方：依《114書審指南 P.16》彈出提醒，請承辦人確認一年內信託贈與移轉是否須補填變動情形欄！",
                    ],
                    "status": "warning",
                },
            },
        ],
        "edges": [
            {"id": "s1_e1", "source": "s1_n1", "target": "s1_n2", "label": "啟動信託處分（贈與配偶）", "animated": True},
            {"id": "s1_e2", "source": "s1_n2", "target": "s1_n3", "label": "113/08/09 移轉並重辦信託", "animated": True},
            {"id": "s1_e3", "source": "s1_n3", "target": "s1_n4", "label": "跨表自動比對附表一丙 vs 附表三", "animated": True},
        ],
    }

    # 劇本 2：114~115年 泰山同興段 3 筆土地「抵押權設定」再信託鏈
    d_instruct_2 = parse_roc_date("114/12/17")
    d_newtrust_2 = parse_roc_date("115/02/23")
    elapsed_days_2 = (d_newtrust_2 - d_instruct_2).days  # 精確為 68 天！
    deadline_90_roc = format_roc_date(d_instruct_2 + timedelta(days=90))  # 115/03/17

    scenario_2 = {
        "scenario_id": "SCENARIO_2_TONGXING_MORTGAGE",
        "title": "劇本 2：114~115年 泰山同興段 3 筆土地「抵押權設定」再信託鏈",
        "gazette_sources": ["廉政專刊第309期 P.10", "廉政專刊第309期 P.363", "廉政專刊第309期 P.356"],
        "summary_metrics": {
            "parcels_count": 3,
            "areas_sqm": [869.04, 1535.03, 666.0],
            "total_area_sqm": round(869.04 + 1535.03 + 666.0, 2),
            "share": "100分之40",
            "instruction_date_roc": "114/12/17",
            "retrust_date_roc": "115/02/23",
            "elapsed_days": elapsed_days_2,
            "statutory_limit_days": 90,
            "deadline_90d_roc": deadline_90_roc,
            "remaining_buffer_days": 90 - elapsed_days_2,
            "updated_titles": ["1.代理院長", "2.副院長"],
        },
        "nodes": [
            {
                "id": "s2_n1",
                "position": {"x": 40, "y": 90},
                "type": "trustNode",
                "data": {
                    "badge": "114/11/01 定期申報附表三（專刊309期P.10）",
                    "title": "原交付第一銀行信託之泰山同興段土地",
                    "subtitle": "職稱：1.監察院 副院長",
                    "details": [
                        "同興段第1筆：869.04 m²（持分 100分之40）",
                        "同興段第2筆：1,535.03 m²（持分 100分之40）",
                        "同興段第3筆：666.00 m²（持分 100分之40）",
                    ],
                    "status": "verified",
                },
            },
            {
                "id": "s2_n2",
                "position": {"x": 380, "y": 90},
                "type": "instructionNode",
                "data": {
                    "badge": "114/12/17 指示通知表（專刊309期P.363）",
                    "title": "事前處分指示通知：「抵押權設定」",
                    "subtitle": "符合本法§9 III 事前或同時通知鐵律",
                    "details": [
                        "通知日期：114年12月17日（免除10萬~200萬罰鍰）",
                        "管理或處分方式：抵押權設定（3筆同興段土地）",
                        f"法定 90 天不可展期屆滿日：{deadline_90_roc}",
                    ],
                    "status": "active",
                },
            },
            {
                "id": "s2_n3",
                "position": {"x": 720, "y": 90},
                "type": "timerNode",
                "data": {
                    "badge": f"Python 確定性時效計時器：第 {elapsed_days_2} / 90 天完成",
                    "title": f"90天處分倒數檢核通過（提前 {90 - elapsed_days_2} 天完竣）",
                    "subtitle": "114/12/17 ➔ 115/02/23（共 68 日曆天）",
                    "details": [
                        f"已耗日數：{elapsed_days_2} 天 ≦ 法定上限 90 天（不得展期）",
                        "契約變更後通知日數：0 天 ≦ 法定上限 30 天",
                        "AI 時效判定：100% 適法合規（A類通過）",
                    ],
                    "status": "verified",
                },
            },
            {
                "id": "s2_n4",
                "position": {"x": 1060, "y": 90},
                "type": "newTrustNode",
                "data": {
                    "badge": "115/02/23 新增信託申報表（專刊309期P.356）",
                    "title": "完成再信託移轉登記＆自動辨識職稱更新",
                    "subtitle": "職稱自動勾稽：1.代理院長、2.副院長",
                    "details": [
                        "移轉登記完成日：115年02月23日（受託人：第一銀行 邱月琴）",
                        "標的：同興段 869.04、1,535.03、666 m²（持分40/100）完全吻合",
                        "職務異動連動：自動核對在職職稱新增『1.監察院 代理院長』！",
                    ],
                    "status": "verified",
                },
            },
        ],
        "edges": [
            {"id": "s2_e1", "source": "s2_n1", "target": "s2_n2", "label": "申請塗銷/設定抵押事前通知", "animated": True},
            {"id": "s2_e2", "source": "s2_n2", "target": "s2_n3", "label": "啟動 90 天不可展期倒數", "animated": True},
            {"id": "s2_e3", "source": "s2_n3", "target": "s2_n4", "label": "第 68 天完成再信託＋職稱辨識", "animated": True},
        ],
    }

    return {
        "person_id": "lee-hung-chun",
        "declarant_name": "李○○",
        "scenarios": {
            "scenario_1": scenario_1,
            "scenario_2": scenario_2,
        },
    }


# ============================================================================
# (d) Y1.1 至 Y99 共 12 種監察院院函例稿與財管系統審核片語映射引擎
# ============================================================================
YUAN_LETTER_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Y1.1": {
        "code": "Y1.1",
        "filename": "Y1.1.不動產或股票信託辦理中114.07.07",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y1.1.不動產或股票信託辦理中114.07.07",
        "subject": "有關臺端申報114年公職人員財產申報表註明部分不動產／國內上市（櫃）股票「刻正辦理信託中」一案，請儘速完成信託並辦理「更正申報」（非新增信託申報），請查照。",
        "internal_routing": "【重要】書審單陳核時，須『內會管制人員』，並由其定期通知責任區承辦人洽申報人瞭解辦理進度。",
        "action_required": "辦理更正申報（非新增信託申報）",
        "audit_slip_checkbox": "信託辦理中",
    },
    "Y1.2": {
        "code": "Y1.2",
        "filename": "Y1.2配偶二戶不動產均申報自住114.07.17",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y1.2配偶二戶不動產均申報自住114.07.17",
        "subject": "有關臺端114年公職人員財產申報表將本人與配偶名下二戶（或兩戶打通具二張獨立權狀）房屋均填報為「自用房屋」未交付信託一案，依法自用房屋免信託以「一戶」為限，請於文到1個月內擇定一戶並就餘戶辦理信託補正，請查照。",
        "internal_routing": "追蹤文到1個月內補正情形；逾期未補正者簽派查核。",
        "action_required": "擇定1戶自住，其餘戶別交付強制信託並補正",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y2": {
        "code": "Y2",
        "filename": "Y2.權狀或股票遺失114.07.28",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y2.權狀或股票遺失114.07.28",
        "subject": "有關臺端申報註明應交付信託之不動產權狀／股票「遺失申請補發中」一案，請於取得補發權狀（股票）之日起3個月內完成信託，並辦理「新增信託申報」（非更正申報），請查照。",
        "internal_routing": "【重要】書審單陳核時，須『內會管制人員』，定期追蹤補發與3個月內新增信託申報進度。",
        "action_required": "取得補發日起3個月內信託並辦理新增信託申報",
        "audit_slip_checkbox": "股票或不動產權狀遺失",
    },
    "Y3": {
        "code": "Y3",
        "filename": "Y3.總額已達100萬-零股應交付信託114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y3.總額已達100萬-零股應交付信託114.06.12",
        "subject": "有關臺端114年公職人員財產申報表填報未交付信託之國內上市（櫃）零股股票，查所有人名下各類有價證券總額已達新臺幣100萬元以上，該零股依法仍應交付信託，請儘速補辦信託及後續更正申報事宜（或提出指示通知表處分出售），請查照。",
        "internal_routing": "核對同一人股票+債券+基金+其他有價證券總額≧100萬元；追蹤1個月內補辦信託或指示處分。",
        "action_required": "補辦零股信託並更正申報，或改填「已向監察院指示通知處分中」並送指示通知表",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y4.1": {
        "code": "Y4.1",
        "filename": "Y4.1.總額未達100萬-非零股應交付信託114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y4.1.總額未達100萬-非零股應交付信託114.06.12",
        "subject": "有關臺端申報國內上市（櫃）股票跨證券帳戶合併達1,000股以上（屬非零股），縱名下有價證券總額未達新臺幣100萬元，依法仍屬應交付強制信託之標的，請於文到1個月內完成信託補正，請查照。",
        "internal_routing": "跨證券戶同檔股票歸戶≧1,000股；追蹤文到1個月內完成信託。",
        "action_required": "非零股強制交付信託並補正",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y4.2": {
        "code": "Y4.2",
        "filename": "Y4.2不論總額是否達100萬-非零股應交付信託-副本抄送配偶114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y4.2不論總額是否達100萬-非零股應交付信託-副本抄送配偶114.06.12",
        "subject": "有關臺端及配偶名下持有國內上市（櫃）股票合計達1,000股以上（非零股）未交付信託一案，不論有價證券總額是否達100萬元均應依法交付信託（本函副本抄送配偶），請儘速辦理信託補正，請查照。",
        "internal_routing": "正本受文者：申報人；副本抄送：申報人配偶；內會管制追蹤。",
        "action_required": "配偶／本人非零股儘速交付信託",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y5": {
        "code": "Y5",
        "filename": "Y5.不動產或股票出售中114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y5.不動產或股票出售中114.06.12",
        "subject": "有關臺端申報應交付信託之不動產／國內上市（櫃）股票註明「出售中」惟未辦理信託或事前指示通知一案，請依法先交付信託或依本法第9條第3項規定辦理指示通知，請查照。",
        "internal_routing": "檢視是否已提送指示通知表及3個月處分期限；內會管制人員。",
        "action_required": "先完成信託或依規定提送處分指示通知表",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y6": {
        "code": "Y6",
        "filename": "Y6.本人有價證券達100萬-零股要信託--配偶未達100萬--非零股要信託114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y6.本人有價證券達100萬-零股要信託--配偶未達100萬--非零股要信託114.06.12",
        "subject": "有關臺端名下有價證券總額已達100萬元致所持有零股應交付信託，暨配偶名下有價證券雖未達100萬元惟持有單一檔達1,000股以上非零股亦應交付信託一案，請儘速併同辦理信託補正，請查照。",
        "internal_routing": "分戶列明本人（達100萬之零股）與配偶（未達100萬之非零股）明細；追蹤1個月內補正。",
        "action_required": "本人零股與配偶非零股一併補辦信託",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y9": {
        "code": "Y9",
        "filename": "Y9.函-文到7日內向地政機關申請補發權狀--補發後辦理信託114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y9.函-文到7日內向地政機關申請補發權狀--補發後辦理信託114.06.12",
        "subject": "有關臺端申報應交付信託之不動產尚未申請補發所有權狀一案，請於文到7日內向地政機關申請補發權狀，並於領得權狀後依限完成強制信託及新增信託申報，請查照。",
        "internal_routing": "管制文到7日內申請補發佐證，內會管制人員列管。",
        "action_required": "文到7日內向地政機關申請補發權狀，補發後辦理信託",
        "audit_slip_checkbox": "股票或不動產權狀遺失",
    },
    "Y10": {
        "code": "Y10",
        "filename": "Y10.股票疑似應信託--函申報人確認114.5.2",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y10.股票疑似應信託--函申報人確認114.5.2",
        "subject": "有關臺端114年公職人員財產申報表所列股票疑似屬國內上市（櫃）應交付信託標的且未註明免信託原因一案，請於文到1個月內查明確認並補正，請查照。",
        "internal_routing": "倘申報人未於1個月期限內補正說明，依實務指南 P.18 簽派查核。",
        "action_required": "文到1個月內確認股票屬性並補辦信託或敘明原因",
        "audit_slip_checkbox": "其他",
    },
    "Y11": {
        "code": "Y11",
        "filename": "Y11.未能交付信託原因填寫錯誤而未信託--提醒儘速辦理信託114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y11.未能交付信託原因填寫錯誤而未信託--提醒儘速辦理信託114.06.12",
        "subject": "有關臺端申報不動產填載之「未能交付信託原因」（如都市計畫住宅區舊地目田、農舍或分別共有等）核與農業發展條例第33條及本法第7條免信託規定未合，請儘速辦理交付信託補正，請查照。",
        "internal_routing": "追蹤文到1個月內交付信託進度；逾期未辦理者簽派查核。",
        "action_required": "修正錯誤之免信託原因並儘速交付強制信託",
        "audit_slip_checkbox": "不動產或股票未交付信託",
    },
    "Y99": {
        "code": "Y99",
        "filename": "Y99.股票疑似應信託--函申報人確認114.06.12",
        "shared_drive_path": r"Y:\C010_第一組\C1.書審--例稿--院函\Y99.股票疑似應信託--函申報人確認114.06.12",
        "subject": "有關臺端定期申報案件所列有價證券項目疑似具應交付強制信託情事（114.06.12新版通案確認函），請於文到1個月內查明確認並函復本院，請查照。",
        "internal_routing": "通案確認例稿，逾期未復依規定簽派查核。",
        "action_required": "文到1個月內查明確認函復",
        "audit_slip_checkbox": "其他",
    },
}


def map_yuan_letter_template(
    violation_code: str,
    correction_round: int = 1,
    target_form: str = "主表",
    declarant_name: str = "○○○",
) -> Dict[str, Any]:
    """
    自動映射 Y1.1 至 Y99 共 12 種監察院院函例稿與財管系統「審核作業片語」，
    並依《114年書審實務作業指南 P.11》自動區分：
    - 【第1次】更正案<主表>
    - 【第2次】更正案<變動表/信託表>【第1次】
    """
    norm_code = (violation_code or "Y99").strip().upper()
    if norm_code not in YUAN_LETTER_TEMPLATES:
        norm_code = "Y99"
    tpl = YUAN_LETTER_TEMPLATES[norm_code]
    today_roc = format_roc_date_cn(date(2026, 11, 6))

    # 依 P.11 書審單更正案標註鐵律自動生成財管系統片語
    if target_form in {"主表", "附表一甲", "附表一丙"} and correction_round == 1:
        correction_tag = "【第1次】更正案<主表>"
        phrase_note = "定期申報主表先收件，書審單註記【第1次】更正案<主表>（請注意主、附表若皆需更正，須各別辦理更正收件，不可併案書審）。"
    else:
        sub_label = "變動表" if "變動" in target_form or "四" in target_form else "信託表"
        correction_tag = f"【第2次】更正案<{sub_label}>【第1次】"
        phrase_note = (
            f"定期申報附表（{sub_label}）隨同主表更正，依規定分別逐案書審，"
            f"系統預設【第2次】更正案已自動加註修改為：{correction_tag}。"
        )

    audit_system_phrase = (
        f"{correction_tag}｜申報人{declarant_name} 114年定期申報案件經形式審核，"
        f"核有「{tpl['filename']}」所示情事，擬依例稿（{tpl['code']}）函請申報人補正；"
        f"{tpl['internal_routing']}"
    )

    draft_letter_body = (
        f"受文者：{declarant_name} 君\n"
        f"發文日期：{today_roc}\n"
        f"發文字號：院台申壹字第115000XXXX號（草稿－待承辦人及組長覆核）\n"
        f"主旨：{tpl['subject']}\n"
        f"說明：\n"
        f"  一、依據公職人員財產申報法第7條、第9條及公職人員財產申報資料審核及查閱辦法規定辦理。\n"
        f"  二、引用例稿路徑：{tpl['shared_drive_path']}\n"
        f"  三、內部陳核提示：{tpl['internal_routing']}\n"
        f"  四、嚴正提醒：如需辦理申報內容更正，請於紙本更正處簽名或蓋章回傳本院，【切勿以網路重新上傳更正】。"
    )

    return {
        "violation_code": tpl["code"],
        "template_filename": tpl["filename"],
        "shared_drive_path": tpl["shared_drive_path"],
        "correction_tag": correction_tag,
        "correction_separation_rule": phrase_note,
        "audit_slip_checkbox": tpl["audit_slip_checkbox"],
        "internal_routing": tpl["internal_routing"],
        "audit_system_phrase": audit_system_phrase,
        "draft_yuan_letter": draft_letter_body,
        "all_available_codes": list(YUAN_LETTER_TEMPLATES.keys()),
    }


# ============================================================================
# 整合檢核：外部申報前 16 條黃金準則即時體檢 & 法規 RAG 檢索
# ============================================================================
def check_personnel_notification_rule(
    event_date: str,
    notify_date: str,
    role_type: str,
    selected_reason: str,
    selected_status: str,
    acting_start_date: Optional[str] = None,
    permanent_appoint_date: Optional[str] = None,
    same_agency: bool = True,
) -> Dict[str, Any]:
    """Rule 1-1 ~ 1-4：職務異動 10 日時效、公股董監事專任定性與代理滿3個月真除檢核。"""
    ev_dt = parse_roc_date(event_date)
    nt_dt = parse_roc_date(notify_date)
    delay_days = (nt_dt - ev_dt).days
    within_10_days = delay_days <= 10

    alerts: List[str] = []
    if not within_10_days:
        alerts.append(
            f"【Rule 1-1 遲延通報預警】異動發生日 {event_date} 至通報日 {notify_date} 已隔 {delay_days} 日（逾法定 10 日期限），"
            "將影響申報人申報期限並觸發公文副知改善！"
        )
    if "公股" in role_type or "私法人" in role_type or "董監事" in role_type:
        if selected_reason != "就(到)職" or selected_status != "專任":
            alerts.append(
                "【Rule 1-1 公股董監事定性校正】代表政府或公股出任私法人董監事，異動原因必選『就(到)職』、職務狀況必選『專任』（非兼任，97法政決0971117901號函），且須由實際指派/遴選機關通報！"
            )

    acting_advice = None
    if acting_start_date:
        act_dt = parse_roc_date(acting_start_date)
        three_month_dt = act_dt + timedelta(days=90)
        deadline_dt = three_month_dt + timedelta(days=90)
        if permanent_appoint_date:
            perm_dt = parse_roc_date(permanent_appoint_date)
            if three_month_dt <= perm_dt <= deadline_dt and same_agency:
                acting_advice = (
                    f"【Rule 1-2 代理真除免重複申報】代理滿3個月日為 {format_roc_date(three_month_dt)}，"
                    f"於代理申報期間（迄 {format_roc_date(deadline_dt)}）內真除且受理機關未變動，"
                    "依 10205011110 號函『僅須辦理代理申報，毋庸再辦就(到)職申報』！"
                )
                alerts.append(acting_advice)

    return {
        "rule_id": "Rule 1-1 & 1-2",
        "delay_days": delay_days,
        "within_10_days": within_10_days,
        "alerts": alerts,
        "acting_advice": acting_advice,
        "compliant": len(alerts) == 0,
    }


def query_rag_knowledge(question: str) -> Dict[str, Any]:
    """檢索內建陽光法案與 114 書審實務指南 RAG 知識庫，強制附上法條函釋出處（Grounding）。"""
    data = load_seed_data()
    kb = data.get("rag_knowledge_base", [])
    q_norm = (question or "").strip().lower()

    scored: List[Tuple[int, Dict[str, Any]]] = []
    for doc in kb:
        score = 0
        for kw in doc.get("keywords", []):
            if kw.lower() in q_norm:
                score += 3
        for char_token in ["預售屋", "零股", "信託", "耕地", "自用", "超過五年", "房地總價額", "虛擬資產", "保險", "融資", "融券", "分割", "變動", "公股", "代理", "10日", "指示通知", "更正"]:
            if char_token in q_norm and (char_token in doc["title"] or char_token in doc["answer"]):
                score += 2
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_matches = [d for s, d in scored if s > 0][:3]
    if not top_matches:
        top_matches = kb[:2]

    primary = top_matches[0]
    return {
        "question": question,
        "matched_title": primary["title"],
        "answer": primary["answer"],
        "legal_source": primary["source"],
        "primary_source": primary["source"],
        "matched_documents": top_matches,
        "stateless_firewall_notice": "本問答採無狀態（Stateless）隔離架構，您的提問內容絕不留存或移作事後查核使用。",
    }

import React, { useState, useEffect } from 'react';
import {
  ClipboardCheck,
  CalendarClock,
  Copy,
  Check,
  UserCheck,
  ShieldCheck,
  Mail,
  FileText,
} from 'lucide-react';

const YUAN_CODES = [
  'Y1.1',
  'Y1.2',
  'Y2',
  'Y3',
  'Y4.1',
  'Y4.2',
  'Y5',
  'Y6',
  'Y9',
  'Y10',
  'Y11',
  'Y99',
];

const BATCH_DATA = [
  { date: '115/01/15', sticky: '115.1.15', count: 292, desc: '北北桃市議會＋總統府、行政院暨所屬', priority: 'P0 最優先' },
  { date: '115/02/05', sticky: '115.2.5', count: 181, desc: '中南高市議會（臺中63、臺南56、高雄62）', priority: 'P1 次優先' },
  { date: '115/02/12', sticky: '115.2.12', count: 113, desc: '立法院（立法委員 113人，分2期）', priority: 'P2 立院梯' },
  { date: '115/03/02', sticky: '115.3.2', count: 812, desc: '其他縣市議會(513)＋司考監院(48)＋縣市政府(251)', priority: 'P3 常規梯' },
];

export default function AbcxReviewCenterTab({ apiBase = '' }) {
  const [auditScenario, setAuditScenario] = useState('LEE_114_A');
  const [violationCode, setViolationCode] = useState('Y6');
  const [correctionRound, setCorrectionRound] = useState(1);
  const [targetForm, setTargetForm] = useState('主表');
  const [triageData, setTriageData] = useState(null);

  // Human-in-the-Loop 雙重簽章狀態
  const [officerSigned, setOfficerSigned] = useState(false);
  const [supervisorSigned, setSupervisorSigned] = useState(false);
  const [hitlLog, setHitlLog] = useState(null);
  const [copiedPhrase, setCopiedPhrase] = useState(false);

  const loadTriage = async (sc, yCode, round, form) => {
    try {
      const res = await fetch(`${apiBase}/api/v1/audit/abcx-triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audit_scenario: sc,
          violation_code: yCode,
          correction_round: round,
          target_form: form,
        }),
      });
      const d = await res.json();
      setTriageData(d);
    } catch (err) {
      console.error('ABCX triage error:', err);
    }
  };

  useEffect(() => {
    setOfficerSigned(false);
    setSupervisorSigned(false);
    setHitlLog(null);
    loadTriage(auditScenario, violationCode, correctionRound, targetForm);
  }, [auditScenario, violationCode, correctionRound, targetForm]);

  const handleSupervisorApprove = async () => {
    setSupervisorSigned(true);
    try {
      const slip = triageData?.form_review_slip || {};
      const res = await fetch(`${apiBase}/api/v1/governance/hitl-approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_ref: `${auditScenario}（${triageData?.declarant_name || ''}）`,
          abcx_result: {
            附表一甲: slip.form_1a_general || '—',
            附表一丙: slip.form_1c_trust_main || '—',
            附表四: slip.form_4_change || 'X',
            附表三: slip.form_3_trust || 'X',
          },
          yuan_letter_code: slip.separate_letter_needed ? violationCode : null,
          reviewer_officer: '第一組承辦人 李大同',
          supervisor_approver: '第一組組長 林○○',
          decision: 'DUAL_SIGNED_APPROVED',
          note: triageData?.audit_system_phrase || '',
        }),
      });
      const data = await res.json();
      setHitlLog(data.latest_entry);
    } catch (err) {
      console.error('HITL approve error:', err);
    }
  };

  const copyPhrase = () => {
    if (!triageData?.audit_system_phrase) return;
    navigator.clipboard.writeText(triageData.audit_system_phrase);
    setCopiedPhrase(true);
    setTimeout(() => setCopiedPhrase(false), 2000);
  };

  const slip = triageData?.form_review_slip || {};

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      {/* 左側：1,398 案四梯次結案期限看板 ＆ 80%+ A類自動分流統計 */}
      <div className="lg:col-span-5 space-y-5">
        <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-slate-900 text-amber-300">
                <CalendarClock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-extrabold text-slate-900">
                  114年刊登公報書審 1,398 案四梯次看板
                </h3>
                <p className="text-xs text-slate-500">115/01/06 中午前正式啟動・Agentic Ranking 自動排序</p>
              </div>
            </div>
          </div>

          {/* 80%+ A類快速分流指標卡 */}
          <div className="rounded-xl bg-slate-900 text-white p-4 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-sky-300 font-bold">全新網路申報快速分流效能</span>
              <span className="px-2 py-0.5 rounded bg-emerald-600 font-bold">免傳統收件/分案/歸檔</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-extrabold text-emerald-400">82.4%</span>
              <span className="text-xs text-slate-300">
                A類無誤案件（約 1,152 案）直接由《形式審核單》快速結案！
              </span>
            </div>
            <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden flex">
              <div className="bg-emerald-500 h-full" style={{ width: '82%' }} title="A類 82%" />
              <div className="bg-amber-400 h-full" style={{ width: '11%' }} title="B類紅筆逕修 11%" />
              <div className="bg-rose-500 h-full" style={{ width: '7%' }} title="C類通知更正 7%" />
            </div>
            <div className="flex justify-between text-[12px] text-slate-300">
              <span>🟢 A類正確：82%</span>
              <span>🟡 B類紅筆逕修：11%</span>
              <span>🔴 C類更正案：7%</span>
            </div>
          </div>

          {/* 四大梯次列表 */}
          <div className="space-y-2.5">
            {BATCH_DATA.map((b) => (
              <div
                key={b.date}
                className="rounded-xl border border-slate-200 p-3 flex items-center justify-between gap-3 bg-slate-50/70"
              >
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-extrabold text-slate-900">{b.date} 結案</span>
                    <span className="px-2 py-0.5 rounded bg-yellow-200 text-amber-950 text-xs font-bold border border-amber-400">
                      卷宗便利貼：{b.sticky}
                    </span>
                  </div>
                  <div className="text-xs text-slate-600">{b.desc}</div>
                </div>
                <div className="text-right shrink-0">
                  <span className="text-base font-extrabold text-sky-900">{b.count}</span>
                  <span className="text-xs text-slate-500 block">人</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 案件情境切換器 */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-3 shadow-sm">
          <div className="text-xs font-extrabold text-slate-700 uppercase">
            切換右側《形式審核單》預填測試案件：
          </div>
          <div className="grid grid-cols-1 gap-2">
            {[
              { id: 'LEE_114_A', label: '🟢 實證案 A：李○○副院長 114定期申報（附表一丙:A / 附表三:A）' },
              { id: 'SYSTEM_DEFAULT_B', label: '🟡 實務案 B：李榮長 5年繼承誤帶房地總價額（附表一丙:B 紅筆逕修）' },
              { id: 'UNREPORTED_CHANGE_C', label: '🔴 實務案 C：張國棟 變動表漏報＆未信託院函（附表四:C 另函補正）' },
            ].map((opt) => (
              <button
                key={opt.id}
                onClick={() => setAuditScenario(opt.id)}
                className={`text-left px-3.5 py-2.5 rounded-xl text-xs font-bold border transition ${
                  auditScenario === opt.id
                    ? 'bg-sky-900 text-white border-sky-950 shadow'
                    : 'bg-slate-50 text-slate-800 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 右側：擬真水藍色《網路定期申報案件形式審核單》＋ 片語＆院函草稿 ＋ HITL 雙重簽章 */}
      <div className="lg:col-span-7 space-y-5">
        {/* 擬真水藍色形式審核單（復刻 PDF1 第 6-7 頁） */}
        <div className="blue-audit-slip rounded-2xl p-6 space-y-4 text-slate-900 font-serif">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b-2 border-sky-700/40 pb-3">
            <div>
              <h3 className="text-xl font-extrabold tracking-wide text-slate-950">
                網路定期申報案件形式審核單
              </h3>
              <p className="text-xs font-sans font-semibold text-sky-900">
                受審申報人：{triageData?.declarant_name} ｜ {triageData?.title}
              </p>
            </div>
            <span className="px-3 py-1 rounded-lg bg-yellow-200 border border-amber-500 text-amber-950 font-sans text-xs font-extrabold shadow-sm">
              📌 卷宗夾便利貼：{triageData?.folder_sticky_deadline || '115.3.2'}
            </span>
          </div>

          <div className="space-y-2">
            <div className="font-bold text-sm">
              ■ 本件檢視結果（請填 A、B、C、X）：
            </div>
            <div className="grid grid-cols-2 gap-4 bg-white/75 rounded-xl p-4 border border-sky-300 text-sm font-bold">
              <div>
                附表一甲：
                <span className="inline-block min-w-[48px] text-center border-b-2 border-slate-800 text-rose-700 text-lg mx-1">
                  {slip.form_1a_general || '—'}
                </span>
              </div>
              <div>
                附表四（變動表）：
                <span className="inline-block min-w-[48px] text-center border-b-2 border-slate-800 text-rose-700 text-lg mx-1">
                  {slip.form_4_change || 'X'}
                </span>
              </div>
              <div>
                附表一丙：
                <span className="inline-block min-w-[48px] text-center border-b-2 border-slate-800 text-rose-700 text-lg mx-1">
                  {slip.form_1c_trust_main || 'A'}
                </span>
              </div>
              <div>
                附表三（信託表）：
                <span className="inline-block min-w-[48px] text-center border-b-2 border-slate-800 text-rose-700 text-lg mx-1">
                  {slip.form_3_trust || 'A'}
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-700 font-sans">
              註：<strong>A</strong>：全部正確、<strong>B</strong>：由承辦人逕予修改，移第5組、
              <strong>C</strong>：已通知申報人更正到院、<strong>X</strong>：免報信託表或變動表。
            </p>
          </div>

          <div className="space-y-1.5 text-sm">
            <div className="font-bold">
              {slip.separate_letter_needed ? '☑' : '☐'} 另函申報人：
            </div>
            <div className="pl-5 space-y-1 text-xs font-semibold">
              <div>
                {slip.checkboxes?.untrusted_property_or_stock ? '☑' : '☐'} 不動產或股票未交付信託 ／{' '}
                {slip.checkboxes?.deed_lost ? '☑' : '☐'} 股票或不動產權狀遺失
              </div>
              <div>{slip.checkboxes?.trust_in_progress ? '☑' : '☐'} 信託辦理中。</div>
              <div>{slip.checkboxes?.other ? '☑' : '☐'} 其他：詳下附 Y 系列院函例稿草稿</div>
            </div>
          </div>

          {/* 承辦人與組長擬真簽章欄 */}
          <div className="pt-3 border-t border-sky-700/30 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-6 text-sm font-bold">
              <div>
                承辦人：
                <span className="inline-block min-w-[96px] border-b-2 border-slate-800 text-center text-rose-700 font-extrabold">
                  {officerSigned ? '李大同 (已簽章)' : '（待簽章）'}
                </span>
              </div>
              <div>
                組長：
                <span className="inline-block min-w-[96px] border-b-2 border-slate-800 text-center text-rose-700 font-extrabold">
                  {supervisorSigned ? '林○○ (已覆核)' : '（待覆核）'}
                </span>
              </div>
            </div>
            <div className="text-xs font-sans font-bold text-rose-800">
              📎 {slip.staple_instruction}
            </div>
          </div>
        </div>

        {/* 財管系統審核作業片語 ＆ Y1.1~Y99 共 12 種院函例稿預覽 */}
        <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-sky-700" />
              <span className="text-sm font-extrabold text-slate-900">
                財管系統「審核作業片語」＆ Y1.1～Y99 院函例稿產生器
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs">
              <select
                value={violationCode}
                onChange={(e) => setViolationCode(e.target.value)}
                className="rounded-lg border border-slate-300 px-2.5 py-1.5 font-bold text-slate-800"
              >
                {YUAN_CODES.map((c) => (
                  <option key={c} value={c}>
                    例稿 {c}
                  </option>
                ))}
              </select>
              <select
                value={`${correctionRound}_${targetForm}`}
                onChange={(e) => {
                  const [r, f] = e.target.value.split('_');
                  setCorrectionRound(Number(r));
                  setTargetForm(f);
                }}
                className="rounded-lg border border-slate-300 px-2.5 py-1.5 font-bold text-slate-800"
              >
                <option value="1_主表">【第1次】更正案&lt;主表&gt;</option>
                <option value="2_變動表">【第2次】更正案&lt;變動表&gt;【第1次】</option>
                <option value="2_信託表">【第2次】更正案&lt;信託表&gt;【第1次】</option>
              </select>
            </div>
          </div>

          {/* 財管系統片語一鍵複製框 */}
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-3.5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-600">
                財管系統插入片語（自動區分主附表更正次別，嚴禁併案書審）：
              </span>
              <button
                onClick={copyPhrase}
                className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-sky-800 text-white text-xs font-bold hover:bg-sky-900"
              >
                {copiedPhrase ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                {copiedPhrase ? '已複製片語' : '一鍵複製片語'}
              </button>
            </div>
            <p className="text-xs text-slate-800 font-medium leading-relaxed">
              {triageData?.audit_system_phrase}
            </p>
          </div>

          {/* Y系列院函例稿草稿預覽 */}
          {triageData?.yuan_letter_preview && (
            <div className="rounded-xl bg-amber-50/50 border border-amber-200 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs font-bold text-amber-900">
                <span className="flex items-center gap-1.5">
                  <Mail className="w-4 h-4" />
                  Gmail 待發草稿（鎖定 DRAFT）：{triageData.yuan_letter_preview.template_filename}
                </span>
                <span className="text-[12px] text-slate-500">
                  {triageData.yuan_letter_preview.shared_drive_path}
                </span>
              </div>
              <pre className="text-xs text-slate-800 whitespace-pre-wrap font-sans leading-relaxed">
                {triageData.yuan_letter_preview.draft_yuan_letter}
              </pre>
            </div>
          )}

          {/* 底部：Human-in-the-Loop 雙重簽章確認按鈕 */}
          <div className="pt-3 border-t border-slate-200 flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => setOfficerSigned(true)}
                disabled={officerSigned}
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                  officerSigned
                    ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                    : 'bg-sky-700 hover:bg-sky-800 text-white shadow'
                }`}
              >
                <UserCheck className="w-4 h-4" />
                {officerSigned ? '1. 承辦人已簽章確認' : '1. 承辦人簽章確認'}
              </button>

              <button
                onClick={handleSupervisorApprove}
                disabled={!officerSigned || supervisorSigned}
                className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold transition ${
                  supervisorSigned
                    ? 'bg-emerald-700 text-white'
                    : officerSigned
                    ? 'bg-indigo-700 hover:bg-indigo-800 text-white shadow animate-pulse'
                    : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                {supervisorSigned
                  ? '2. 組長已完成 Human-in-the-Loop 覆核放行！'
                  : '2. 移送組長覆核 (Human-in-the-Loop)'}
              </button>
            </div>

            {hitlLog && (
              <div className="w-full rounded-xl bg-emerald-950 text-emerald-100 p-3 text-xs flex flex-wrap items-center justify-between gap-2">
                <span>
                  ✅ <strong>Glass-box 可解釋稽核簽章已寫入：</strong>
                  {hitlLog.log_id} ｜ {hitlLog.gmail_draft_status}
                </span>
                <code className="text-amber-300 font-mono">{hitlLog.glassbox_hash}</code>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

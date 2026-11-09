import React, { useState, useEffect } from 'react';
import {
  Sun,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ArrowRight,
  Coins,
  Scale,
  BookOpen,
  Send,
  Lock,
  Calculator,
  FileCheck2,
  RotateCcw,
} from 'lucide-react';

const FEATURED_CARDS = [
  { id: 'B1', badge: '案例 1', title: '預售屋填備註欄僅報已付290萬', fine: '45萬', rule: 'Rule 2-2' },
  { id: 'B4', badge: '案例 2', title: '土地地號0005分割出售漏報變動', fine: '120萬', rule: 'Rule 3-2/3-3' },
  { id: 'B5', badge: '案例 3', title: '融資買台積電漏報1,503萬融資債務', fine: '32萬', rule: 'Rule 2-6' },
  { id: 'B9', badge: '案例 4', title: '跨證券戶中鋼800+400股與台積電200股零股試算', fine: '36萬', rule: 'Rule 4-2' },
  { id: 'B8', badge: '案例 5', title: '假耕地（地目田/農舍）與雙權狀打通自住屋檢核', fine: '60萬', rule: 'Rule 4-1' },
  { id: 'N1', badge: '案例 6', title: '職務異動10日通報與代理真除定性', fine: '12萬', rule: 'Rule 1-1/1-2' },
  { id: 'B10', badge: '案例 7', title: '處分前指示通知鐵律＆切換頁籤遺失信託合約PDF防呆', fine: '50萬', rule: 'Rule 4-3/4-4' },
];

const EXTRA_B_CASES = [
  { id: 'B2', label: '【擴充案例 B2】基準日前夕領現 140+30 萬放家中未報（Rule 2-3）' },
  { id: 'B3', label: '【擴充案例 B3】漏報未上市船舶股票 3,990 萬 vs 配偶有限公司出資 45 萬（Rule 2-4）' },
  { id: 'B6', label: '【擴充案例 B6】5B 利息所得私人借貸 3,600 萬債權與謄本抵押債務 900 萬（Rule 2-6）' },
  { id: 'B7', label: '【擴充案例 B7】跨年財產增 1,170 萬逾全家所得 458 萬之 1 倍預警（Rule 2-6）' },
];

const QUICK_RAG_QUESTIONS = [
  '預售屋已經寫在備註欄並填已付工程款290萬，為什麼還會被罰？',
  '不同券商帳戶的中鋼800股與400股算零股嗎？台積電200股要信託嗎？',
  '都市計畫住宅區「地目：田」或兩戶打通自住可以免信託嗎？',
  '114年新制虛擬資產（加密貨幣）多少錢要申報？必填什麼欄位？',
];

export default function SunshineGuidancePod({ apiBase = '' }) {
  const [selectedId, setSelectedId] = useState('B1');
  const [caseResult, setCaseResult] = useState(null);
  const [isRemediated, setIsRemediated] = useState(false);
  const [loading, setLoading] = useState(false);

  // 法規 RAG 檢索狀態
  const [ragQuestion, setRagQuestion] = useState(QUICK_RAG_QUESTIONS[0]);
  const [ragResult, setRagResult] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  const loadScenario = async (cid) => {
    setSelectedId(cid);
    setIsRemediated(false);
    setLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/guidance/pre-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ case_id: cid }),
      });
      const data = await res.json();
      setCaseResult(data);
    } catch (err) {
      console.error('Pre-check API error:', err);
    } finally {
      setLoading(false);
    }
  };

  const askRag = async (qText) => {
    const queryStr = qText || ragQuestion;
    setRagQuestion(queryStr);
    setRagLoading(true);
    try {
      const res = await fetch(`${apiBase}/api/v1/rag/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: queryStr }),
      });
      const data = await res.json();
      setRagResult(data);
    } catch (err) {
      console.error('RAG query error:', err);
    } finally {
      setRagLoading(false);
    }
  };

  useEffect(() => {
    loadScenario('B1');
    askRag(QUICK_RAG_QUESTIONS[0]);
  }, []);

  const currentSeverity = isRemediated ? 'GREEN' : caseResult?.severity || 'RED';

  return (
    <div className="space-y-6">
      {/* 頂部無狀態防火牆安心橫幅 */}
      <div className="rounded-2xl bg-gradient-to-r from-amber-50 via-emerald-50 to-amber-50 border border-amber-200 p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-amber-500 text-white shadow">
            <Sun className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-amber-950">
              良醫治未病・源頭防罰主動輔導艙（申報人＆人事政風通報端）
            </h2>
            <p className="text-sm text-amber-900/80">
              於 12 月 5 日授權介接資料下載及上傳前即時攔截「未介接財產盲區」，以溫暖輔導處方箋取代事後高額裁罰。
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 bg-emerald-700 text-white px-3.5 py-2 rounded-xl text-xs font-semibold shadow-sm">
          <Lock className="w-4 h-4" />
          <span>Stateless 輔導防火牆：預檢紀錄零留存・絕不作為事後查核依據</span>
        </div>
      </div>

      {/* 主網格：左側 10 大情境模擬器 + 右側 AI 申報體檢與溫馨處方箋 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 左側：7 張精選案例卡片 + 擴充 B1~B10 下拉選單 */}
        <div className="lg:col-span-5 bg-white rounded-2xl border border-amber-200/80 shadow-sm p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-amber-100 pb-3">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-amber-700">
                Track B Simulator
              </span>
              <h3 className="text-base font-bold text-slate-900">
                10 大高頻誤報與裁罰情境模擬器
              </h3>
            </div>
            <span className="text-xs px-2.5 py-1 rounded-full bg-amber-100 text-amber-900 font-semibold">
              16 條黃金準則即時掃描
            </span>
          </div>

          <div className="space-y-2.5">
            {FEATURED_CARDS.map((card) => {
              const active = selectedId === card.id;
              return (
                <button
                  key={card.id}
                  onClick={() => loadScenario(card.id)}
                  className={`w-full text-left p-3.5 rounded-xl border transition-all flex items-center justify-between gap-3 ${
                    active
                      ? 'bg-amber-50 border-amber-500 ring-2 ring-amber-400/40 shadow-sm'
                      : 'bg-slate-50/60 border-slate-200 hover:border-amber-300 hover:bg-amber-50/40'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 text-xs font-bold rounded bg-amber-600 text-white">
                        {card.badge}
                      </span>
                      <span className="text-xs font-semibold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">
                        {card.rule}
                      </span>
                    </div>
                    <p className="text-sm font-bold text-slate-900">{card.title}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <span className="text-xs text-slate-500 block">規避罰鍰</span>
                    <span className="text-sm font-extrabold text-rose-600">{card.fine}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* 完整 10 大裁罰集擴充選單 */}
          <div className="pt-2 border-t border-amber-100">
            <label className="block text-xs font-bold text-slate-600 mb-1.5">
              更多宣導簡報裁罰攔截案例（B2 / B3 / B6 / B7）：
            </label>
            <select
              value={EXTRA_B_CASES.some((c) => c.id === selectedId) ? selectedId : ''}
              onChange={(e) => e.target.value && loadScenario(e.target.value)}
              className="w-full rounded-xl border border-amber-300 bg-amber-50/50 px-3 py-2 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="">-- 點此載入更多未介接盲區案例 (共11組完整收錄) --</option>
              {EXTRA_B_CASES.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 右側：AI 申報體檢與溫馨輔導處方箋 */}
        <div className="lg:col-span-7 bg-white rounded-2xl border border-emerald-200 shadow-sm p-6 space-y-5">
          {loading || !caseResult ? (
            <div className="py-16 text-center text-slate-500 text-sm">
              正在啟動純 Python 確定性引擎與陽光智導 Agent 體檢中...
            </div>
          ) : (
            <>
              {/* 三色風險燈號與規避裁罰金額徽章 */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  {currentSeverity === 'RED' && (
                    <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-rose-100 text-rose-800 font-bold text-sm border border-rose-300 animate-pulse">
                      <ShieldAlert className="w-4 h-4 text-rose-600" />
                      紅燈高風險攔截（上傳前必修正）
                    </span>
                  )}
                  {currentSeverity === 'ORANGE' && (
                    <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-900 font-bold text-sm border border-amber-300">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      橙燈異常預警（建議核對補正）
                    </span>
                  )}
                  {currentSeverity === 'GREEN' && (
                    <span className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-100 text-emerald-900 font-bold text-sm border border-emerald-400">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      綠燈體檢通過！欄位與價額已精準修正
                    </span>
                  )}
                  <span className="text-xs font-semibold text-slate-500">
                    申報人：{caseResult.declarant}
                  </span>
                </div>

                <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-sm">
                  <Coins className="w-4 h-4 text-amber-300" />
                  <span className="text-xs font-medium">成功規避潛在裁罰：</span>
                  <span className="text-base font-extrabold text-amber-200">
                    NT$ {(caseResult.potential_fine_avoided_ntd || 0).toLocaleString()} 元
                  </span>
                </div>
              </div>

              {/* 農業生產履歷輔導員溫馨處方箋 */}
              <div className="rounded-2xl bg-amber-50/90 border border-amber-200 p-4 space-y-3">
                <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                  <Sparkles className="w-4 h-4 text-amber-600" />
                  <span>陽光智導員溫馨輔導處方箋（{caseResult.rule_id}）</span>
                </div>
                <p className="text-sm leading-relaxed text-slate-800 font-medium">
                  {caseResult.warm_prescription}
                </p>
                <div className="flex items-start gap-2 pt-2 border-t border-amber-200/70 text-xs text-amber-950/80">
                  <Scale className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                  <span>
                    <strong>法源與實務判決依據：</strong>
                    {caseResult.legal_basis}
                  </span>
                </div>
              </div>

              {/* 修正前 vs 修正後 跨欄位動態對照區 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  className={`rounded-xl p-4 border ${
                    isRemediated
                      ? 'bg-slate-50 border-slate-200 opacity-60'
                      : 'bg-rose-50/60 border-rose-300'
                  }`}
                >
                  <div className="text-xs font-bold text-rose-700 mb-1">
                    ❌ 原始申報草稿（誤報／漏報狀態）
                  </div>
                  <div className="text-xs font-semibold text-slate-700 mb-1">
                    欄位：{caseResult.draft_before?.section}
                  </div>
                  <p className="text-sm text-slate-800 leading-relaxed">
                    {caseResult.draft_before?.item_name}
                  </p>
                </div>

                <div
                  className={`rounded-xl p-4 border transition-all ${
                    isRemediated
                      ? 'bg-emerald-50 border-emerald-500 ring-2 ring-emerald-400/40 shadow-md'
                      : 'bg-emerald-50/40 border-emerald-200 border-dashed'
                  }`}
                >
                  <div className="text-xs font-bold text-emerald-800 mb-1 flex items-center gap-1.5">
                    <FileCheck2 className="w-4 h-4" />
                    {isRemediated ? '✅ 已完成自動搬移與價額修正！' : '✨ AI 建議自動轉換後正確欄位'}
                  </div>
                  <div className="text-xs font-semibold text-emerald-900 mb-1">
                    目標欄位：{caseResult.draft_after?.section}
                  </div>
                  <p className="text-sm text-slate-900 font-medium leading-relaxed">
                    {caseResult.draft_after?.item_name}
                  </p>
                </div>
              </div>

              {/* 若為 B9 跨證券戶零股歸戶案例，展開純 Python 確定性計算明細 */}
              {caseResult.deterministic_proof?.odd_lot_calculation && (
                <div className="rounded-xl bg-slate-900 text-slate-100 p-4 space-y-2 text-xs">
                  <div className="flex items-center justify-between text-amber-300 font-bold">
                    <span className="flex items-center gap-1.5">
                      <Calculator className="w-4 h-4" />
                      純 Python 跨證券戶零股歸戶＆100萬門檻確定性計算引擎 (`check_odd_lot_trust`)
                    </span>
                    <span className="px-2 py-0.5 rounded bg-emerald-600 text-white">零心算幻覺</span>
                  </div>
                  {Object.entries(
                    caseResult.deterministic_proof.odd_lot_calculation.per_owner_summary
                  ).map(([owner, info]) => (
                    <div key={owner} className="border-t border-slate-700 pt-2 space-y-1">
                      <div className="font-bold text-emerald-300">
                        ▶ {owner}｜名下有價證券總額：NT${' '}
                        {info.breakdown_ntd.total_securities_ntd.toLocaleString()} 元（
                        {info.reaches_1m_threshold ? '≧ 100萬門檻' : '< 100萬門檻'}）
                      </div>
                      {info.tickers.map((t) => (
                        <div key={t.ticker} className="pl-3 text-slate-300">
                          • {t.ticker}：跨戶合計 <strong>{t.total_shares} 股</strong> ➔{' '}
                          <span className="text-amber-300 font-semibold">{t.lot_category}</span>（對映院函：
                          {t.yuan_letter_code || '免發函'}）
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              )}

              {/* 一鍵自動搬移/修正欄位互動按鈕 */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                {!isRemediated ? (
                  <button
                    onClick={() => setIsRemediated(true)}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-emerald-600 hover:from-amber-600 hover:to-emerald-700 text-white font-bold text-sm shadow-md transition-all"
                  >
                    <Sparkles className="w-4 h-4" />
                    一鍵自動搬移／修正申報草稿欄位
                    <ArrowRight className="w-4 h-4" />
                  </button>
                ) : (
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-emerald-700 flex items-center gap-1.5">
                      <CheckCircle2 className="w-5 h-5" />
                      已套用修正處方！您現在可安心透過自然人憑證同步上傳申報表。
                    </span>
                    <button
                      onClick={() => setIsRemediated(false)}
                      className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-semibold text-slate-600 hover:bg-slate-100"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      還原對照
                    </button>
                  </div>
                )}
                <span className="text-xs text-slate-400">
                  協同代理：{caseResult.invoked_agents?.join(' ➔ ')}
                </span>
              </div>
            </>
          )}
        </div>
      </div>

      {/* 下方：陽光法案 RAG 法規條文與函釋智慧檢索問答介面 */}
      <div className="bg-white rounded-2xl border border-amber-200 shadow-sm p-6 space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-emerald-600 text-white">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                陽光法案＆書審實務指南 RAG 法規條文檢索問答助手
              </h3>
              <p className="text-xs text-slate-500">
                強制綁定《公職人員財產申報法》、施行細則、法務部函釋與行政法院判決出處（Grounding 防幻覺）
              </p>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          {QUICK_RAG_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => askRag(q)}
              className="text-xs px-3 py-1.5 rounded-full bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-200 font-medium transition"
            >
              💡 {q}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            type="text"
            value={ragQuestion}
            onChange={(e) => setRagQuestion(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && askRag(ragQuestion)}
            placeholder="請輸入財產申報法規疑義（如：預售屋、零股100萬信託、耕地認定、虛擬資產錢包地址、代理真除）..."
            className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />
          <button
            onClick={() => askRag(ragQuestion)}
            disabled={ragLoading}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-sm"
          >
            <Send className="w-4 h-4" />
            檢索解答
          </button>
        </div>

        {ragResult && (
          <div className="rounded-xl bg-emerald-50/70 border border-emerald-200 p-4 space-y-2">
            <div className="text-xs font-bold text-emerald-800">
              📌 權威法源出處：{ragResult.primary_source}
            </div>
            <p className="text-sm text-slate-800 whitespace-pre-line leading-relaxed">
              {ragResult.answer}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

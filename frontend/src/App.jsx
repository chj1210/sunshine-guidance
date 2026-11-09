import React, { useState, useEffect } from 'react';
import { Sun, Shield, Award, Activity, CheckCircle2, Cpu, Clapperboard } from 'lucide-react';
import SunshineGuidancePod from './components/SunshineGuidancePod';
import IntegrityAuditDesk from './components/IntegrityAuditDesk';

export default function App() {
  const [mode, setMode] = useState('GUIDANCE'); // 'GUIDANCE' | 'AUDIT'
  const [auditTab, setAuditTab] = useState('A');
  const [showMissionModal, setShowMissionModal] = useState(false);
  const [showDirectorBar, setShowDirectorBar] = useState(true);
  const [activeScene, setActiveScene] = useState(1);

  const jumpScene = (sceneNo) => {
    setActiveScene(sceneNo);
    if (sceneNo === 1) {
      setMode('GUIDANCE');
      setShowMissionModal(true);
    } else if (sceneNo === 2) {
      setMode('GUIDANCE');
      setShowMissionModal(false);
    } else if (sceneNo === 3) {
      setMode('AUDIT');
      setShowMissionModal(false);
      setAuditTab('A');
    } else if (sceneNo === 4) {
      setMode('AUDIT');
      setShowMissionModal(false);
      setAuditTab('C');
    }
  };

  useEffect(() => {
    const onKey = (e) => {
      if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) return;
      if (e.key === 'h' || e.key === 'H') setShowDirectorBar((v) => !v);
      if (['1', '2', '3', '4'].includes(e.key)) jumpScene(Number(e.key));
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);

  const isGuidance = mode === 'GUIDANCE';

  return (
    <div
      className={`min-h-screen transition-colors duration-300 ${
        isGuidance
          ? 'bg-gradient-to-br from-amber-50/60 via-stone-50 to-emerald-50/50 text-slate-900'
          : 'bg-gradient-to-br from-slate-100 via-slate-50 to-sky-50/40 text-slate-900'
      }`}
    >
      {/* 🎬 競賽 3 分鐘 Demo 錄影分鏡導播列（按鍵盤 H 可隱藏/喚回） */}
      {showDirectorBar && (
        <div className="bg-slate-950 text-slate-100 border-b border-amber-400/30 px-4 py-1.5 text-xs">
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
            <div className="flex flex-wrap items-center gap-1.5">
              <span className="inline-flex items-center gap-1 font-extrabold text-amber-400 mr-1">
                <Clapperboard className="w-3.5 h-3.5" />
                3分鐘錄影分鏡快切：
              </span>
              {[
                { id: 1, label: '[1] 0:00 破題＆AI治理面板' },
                { id: 2, label: '[2] 0:30 陽光智導艙（預售屋＆零股防罰）' },
                { id: 3, label: '[3] 1:30 廉政護航台（李○○圖譜＆紅筆 √/★）' },
                { id: 4, label: '[4] 2:25 ABCX天藍審核單＆HITL雙重蓋章' },
              ].map((sc) => (
                <button
                  key={sc.id}
                  onClick={() => jumpScene(sc.id)}
                  className={`px-3 py-1 rounded-full font-bold transition ${
                    activeScene === sc.id
                      ? 'bg-gradient-to-r from-amber-400 to-emerald-400 text-slate-950 shadow'
                      : 'bg-white/10 hover:bg-white/20 text-slate-200'
                  }`}
                >
                  {sc.label}
                </button>
              ))}
            </div>
            <button
              onClick={() => setShowDirectorBar(false)}
              className="px-2.5 py-0.5 rounded-full bg-white/10 hover:bg-white/20 text-slate-300"
            >
              隱藏導播列 [H]
            </button>
          </div>
        </div>
      )}
      {/* 頂部導覽列 (Dual-Mode Switcher + 自主實作+2分標章 + Glass-box AI治理狀態燈) */}
      <header
        className={`sticky top-0 z-40 border-b backdrop-blur-md transition-colors ${
          isGuidance
            ? 'bg-amber-950/95 border-amber-800 text-amber-50'
            : 'bg-slate-950/95 border-slate-800 text-slate-50'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex flex-wrap items-center justify-between gap-4">
          {/* 品牌標題 */}
          <div className="flex items-center gap-3">
            <div
              className={`p-2 rounded-xl shadow ${
                isGuidance ? 'bg-amber-500 text-slate-950' : 'bg-sky-600 text-white'
              }`}
            >
              {isGuidance ? <Sun className="w-6 h-6" /> : <Shield className="w-6 h-6" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold tracking-wider uppercase text-amber-300">
                  監察院公職人員財產申報處・115年AI卓越應用競賽 POC
                </span>
              </div>
              <h1 className="text-base sm:text-lg font-extrabold tracking-tight">
                陽光智導・廉政護航：公職人員財產申報雙向賦能平臺
              </h1>
            </div>
          </div>

          {/* 中央醒目雙模式切換器 (Dual-Mode Switcher) */}
          <div className="flex items-center p-1 rounded-2xl bg-black/30 border border-white/15">
            <button
              onClick={() => setMode('GUIDANCE')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold transition-all ${
                isGuidance
                  ? 'bg-gradient-to-r from-amber-400 to-emerald-500 text-slate-950 shadow-md'
                  : 'text-slate-300 hover:text-white'
              }`}
            >
              <span>☀️ 模式一：陽光智導艙</span>
              <span className="hidden xl:inline text-[12px] font-semibold opacity-85">
                （事前治未病）
              </span>
            </button>
            <button
              onClick={() => setMode('AUDIT')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs sm:text-sm font-extrabold transition-all ${
                !isGuidance
                  ? 'bg-gradient-to-r from-sky-500 to-indigo-600 text-white shadow-md'
                  : 'text-amber-200/80 hover:text-white'
              }`}
            >
              <span>🛡️ 模式二：廉政護航台</span>
              <span className="hidden xl:inline text-[12px] font-semibold opacity-85">
                （跨期勾稽＆ABCX）
              </span>
            </button>
          </div>

          {/* 右上角常駐標章區 */}
          <div className="flex items-center gap-2.5">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-400/20 border border-amber-300/50 text-amber-200 text-xs font-extrabold">
              <Award className="w-4 h-4 text-amber-300 shrink-0" />
              <span>公務同仁自主實作（零委外預算）+2分</span>
            </div>

            <button
              onClick={() => setShowMissionModal(!showMissionModal)}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/30 border border-emerald-400/50 text-emerald-200 text-xs font-bold transition"
            >
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
              <Activity className="w-4 h-4 text-emerald-300" />
              <span>Mission Control: Glass-box AI 治理</span>
            </button>
          </div>
        </div>
      </header>

      {/* Glass-box AI 治理狀態彈出面板 */}
      {showMissionModal && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 pt-4">
          <div className="rounded-2xl bg-slate-900 text-slate-100 border border-emerald-500/40 p-5 shadow-xl space-y-3">
            <div className="flex items-center justify-between border-b border-slate-700 pb-2">
              <div className="flex items-center gap-2 text-sm font-extrabold text-emerald-300">
                <Cpu className="w-5 h-5" />
                <span>
                  Google ADK 五大協同 Agent ＆ Glass-box 可解釋性治理監控面板
                </span>
              </div>
              <button
                onClick={() => setShowMissionModal(false)}
                className="text-xs text-slate-400 hover:text-white"
              >
                收合面板 ✕
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
              {[
                {
                  title: '1. 零幻覺確定性計算',
                  desc: '所有 5 年期間、跨戶零股 100 萬門檻與 68/90 天時效均由純 Python 執行，嚴禁 LLM 心算。',
                },
                {
                  title: '2. 輔導與查核防火牆',
                  desc: '陽光智導艙採 Stateless 無狀態隔離，申報人預檢草稿與提問絕不留存供事後裁罰。',
                },
                {
                  title: '3. 地端封閉主權 AI',
                  desc: '支援 TAIDE / 本地端模型部署，敏感財產個資不出監察院內網（安全可信賴 AI +2分）。',
                },
                {
                  title: '4. Human-in-the-Loop',
                  desc: 'Y1.1~Y99 院函與更正通知強制鎖定為 Gmail 草稿，須經承辦人與組長雙重簽章始放行。',
                },
              ].map((g) => (
                <div key={g.title} className="rounded-xl bg-slate-800/90 p-3 border border-slate-700">
                  <div className="font-bold text-amber-300 flex items-center gap-1.5 mb-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    {g.title}
                  </div>
                  <p className="text-slate-300 leading-relaxed">{g.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 主內容容器 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {isGuidance ? <SunshineGuidancePod /> : <IntegrityAuditDesk externalTab={auditTab} />}
      </main>
    </div>
  );
}

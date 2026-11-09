import React, { useState, useEffect } from 'react';
import { GitBranch, PenTool, ClipboardCheck } from 'lucide-react';
import AssetFlowGraphTab from './AssetFlowGraphTab';
import RedPencilPreviewTab from './RedPencilPreviewTab';
import AbcxReviewCenterTab from './AbcxReviewCenterTab';

export default function IntegrityAuditDesk({ apiBase = '', externalTab = null }) {
  const [subTab, setSubTab] = useState('A');

  useEffect(() => {
    if (externalTab) setSubTab(externalTab);
  }, [externalTab]);

  const tabs = [
    {
      id: 'A',
      label: '子頁籤 A：跨期動態資產軌跡圖譜 (Asset Graph)',
      icon: GitBranch,
    },
    {
      id: 'B',
      label: '子頁籤 B：B類紅鉛筆逕修 (√) 與 C類星號更正 (★)',
      icon: PenTool,
    },
    {
      id: 'C',
      label: '子頁籤 C：形式審核單 (ABCX) 與 HITL 覆核中心',
      icon: ClipboardCheck,
    },
  ];

  return (
    <div className="space-y-6">
      {/* 三幕劇子頁籤切換列 */}
      <div className="bg-slate-900 p-2 rounded-2xl flex flex-wrap gap-2 shadow-md">
        {tabs.map((t) => {
          const Icon = t.icon;
          const active = subTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setSubTab(t.id)}
              className={`flex-1 min-w-[240px] flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                active
                  ? 'bg-sky-600 text-white shadow-lg ring-2 ring-sky-300/40'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {subTab === 'A' && <AssetFlowGraphTab apiBase={apiBase} />}
      {subTab === 'B' && <RedPencilPreviewTab />}
      {subTab === 'C' && <AbcxReviewCenterTab apiBase={apiBase} />}
    </div>
  );
}

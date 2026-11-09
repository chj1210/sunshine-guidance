import React, { useState, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Handle,
  Position,
} from '@xyflow/react';
import {
  GitBranch,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  UserCheck,
} from 'lucide-react';

function CustomAuditNode({ data }) {
  const statusStyles = {
    verified: 'border-emerald-500 bg-white',
    active: 'border-sky-500 bg-sky-50/90',
    warning: 'border-amber-500 bg-amber-50',
  };
  const badgeStyles = {
    verified: 'bg-emerald-700 text-white',
    active: 'bg-sky-700 text-white',
    warning: 'bg-amber-600 text-white',
  };
  const st = data.status || 'verified';

  return (
    <div
      className={`w-[300px] rounded-2xl border-2 shadow-lg p-4 space-y-2 ${statusStyles[st]}`}
    >
      <Handle type="target" position={Position.Left} className="!bg-slate-600 !w-3 !h-3" />
      <div className="flex items-center justify-between gap-2">
        <span className={`text-xs font-bold px-2.5 py-0.5 rounded-md ${badgeStyles[st]}`}>
          {data.badge}
        </span>
        {st === 'warning' ? (
          <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
        ) : (
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
        )}
      </div>
      <div className="text-sm font-extrabold text-slate-900">{data.title}</div>
      <div className="text-xs font-semibold text-sky-900">{data.subtitle}</div>
      <ul className="space-y-1 pt-1 border-t border-slate-200 text-xs text-slate-700">
        {(data.details || []).map((line, idx) => (
          <li key={idx} className="leading-snug">
            • {line}
          </li>
        ))}
      </ul>
      <Handle type="source" position={Position.Right} className="!bg-slate-600 !w-3 !h-3" />
    </div>
  );
}

export default function AssetFlowGraphTab({ apiBase = '' }) {
  const [scenarioKey, setScenarioKey] = useState('scenario_1');
  const [graphBundle, setGraphBundle] = useState(null);

  const nodeTypes = useMemo(
    () => ({
      trustNode: CustomAuditNode,
      instructionNode: CustomAuditNode,
      newTrustNode: CustomAuditNode,
      timerNode: CustomAuditNode,
      auditAlertNode: CustomAuditNode,
    }),
    []
  );

  useEffect(() => {
    fetch(`${apiBase}/api/v1/audit/asset-graph/lee-hung-chun`)
      .then((r) => r.json())
      .then((d) => setGraphBundle(d))
      .catch((err) => console.error('Asset graph load error:', err));
  }, [apiBase]);

  const activeScenario = graphBundle?.scenarios?.[scenarioKey];

  return (
    <div className="space-y-5">
      {/* 劇本切換列 */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-slate-900 text-sky-300">
            <GitBranch className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              李○○副院長（代理院長）111～115 年公報跨期動態資產軌跡圖譜
            </h3>
            <p className="text-xs text-slate-500">
              自動串聯《附表一丙》、《附表三》、《指示通知表》與《新增信託財產申報表》執行跨年跨表勾稽
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setScenarioKey('scenario_1')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${scenarioKey === 'scenario_1'
                ? 'bg-sky-800 text-white shadow'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
          >
            劇本 1：111~113年 淡水竹圍段房地「配偶贈與」移轉鏈
          </button>
          <button
            onClick={() => setScenarioKey('scenario_2')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${scenarioKey === 'scenario_2'
                ? 'bg-sky-800 text-white shadow'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
          >
            劇本 2：114~115年 泰山同興段3筆土地「抵押權設定」再信託鏈（68/90天）
          </button>
        </div>
      </div>

      {/* 劇本關鍵數據指標列 */}
      {activeScenario && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-3">
            <FileSpreadsheet className="w-8 h-8 text-sky-700 shrink-0" />
            <div>
              <div className="text-xs text-slate-500 font-semibold">真實公報驗證出處</div>
              <div className="text-xs font-bold text-slate-900">
                {activeScenario.gazette_sources.join(' ／ ')}
              </div>
            </div>
          </div>

          {scenarioKey === 'scenario_1' ? (
            <>
              <div className="bg-white rounded-xl border border-slate-200 p-4 flex items-center gap-3">
                <UserCheck className="w-8 h-8 text-emerald-600 shrink-0" />
                <div>
                  <div className="text-xs text-slate-500 font-semibold">跨表所有權移轉軌跡</div>
                  <div className="text-sm font-extrabold text-slate-900">
                    李○○ ➔ 配偶 劉○○（竹圍段 3,305.58 m²）
                  </div>
                </div>
              </div>
              <div className="bg-amber-50 rounded-xl border border-amber-300 p-4 flex items-center gap-3">
                <AlertCircle className="w-8 h-8 text-amber-600 shrink-0" />
                <div>
                  <div className="text-xs text-amber-800 font-bold">跨表勾稽關鍵發現</div>
                  <div className="text-xs font-semibold text-amber-950">
                    113/11/01 附表一丙「土地/建物變動情形」欄空白 ➔ 自動提醒書審覆核
                  </div>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="bg-emerald-50 rounded-xl border border-emerald-300 p-4 flex items-center gap-3">
                <Clock className="w-8 h-8 text-emerald-700 shrink-0" />
                <div className="w-full">
                  <div className="flex justify-between text-xs font-bold text-emerald-900 mb-1">
                    <span>90天不可展期處分計時器</span>
                    <span>第 68 天完竣（剩餘 22 天緩衝）</span>
                  </div>
                  <div className="w-full h-2.5 bg-emerald-200 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-600 rounded-full" style={{ width: '75.5%' }} />
                  </div>
                </div>
              </div>
              <div className="bg-sky-50 rounded-xl border border-sky-300 p-4 flex items-center gap-3">
                <UserCheck className="w-8 h-8 text-sky-700 shrink-0" />
                <div>
                  <div className="text-xs text-sky-800 font-bold">115/02/23 職稱自動勾稽更新</div>
                  <div className="text-sm font-extrabold text-slate-900">
                    1. 監察院 代理院長 ／ 2. 副院長
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* React Flow 互動畫布 */}
      <div className="h-[430px] w-full bg-slate-900 rounded-2xl border border-slate-700 overflow-hidden shadow-inner">
        {activeScenario ? (
          <ReactFlow
            nodes={activeScenario.nodes}
            edges={activeScenario.edges}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#334155" gap={20} />
            <Controls />
            <MiniMap nodeColor="#0284c7" maskColor="rgba(15, 23, 42, 0.7)" />
          </ReactFlow>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-400 text-sm">
            載入跨期知識圖譜中...
          </div>
        )}
      </div>
    </div>
  );
}

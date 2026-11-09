import React, { useState } from 'react';
import {
  PenTool,
  ShieldCheck,
  Ban,
  Printer,
  CheckCircle2,
  Eye,
  StickyNote,
} from 'lucide-react';

export default function RedPencilPreviewTab() {
  const [showOverlay, setShowOverlay] = useState(true);

  return (
    <div className="space-y-6">
      {/* 頂部操作列 */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 flex flex-wrap items-center justify-between gap-4 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-rose-600 text-white">
            <PenTool className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              B類紅鉛筆逕修（`√`）與 C類星號更正（`★`）智慧標記預覽台
            </h3>
            <p className="text-xs text-slate-500">
              精準復刻《114年書審實務作業指南 P.12-17, P.26-27》：區分「承辦人紅筆逕修移第5組」與「傳真申報人簽章回傳打星號」
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowOverlay(!showOverlay)}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold border transition ${showOverlay
            ? 'bg-rose-600 text-white border-rose-700 shadow'
            : 'bg-slate-100 text-slate-700 border-slate-300'
            }`}
        >
          <Eye className="w-4 h-4" />
          {showOverlay ? '顯示 AI 紅鉛筆批改＆便利貼圖層（開啟中）' : '點此開啟 AI 紅鉛筆批改圖層'}
        </button>
      </div>

      {/* 實證區塊 1：李○○副院長 114/11/01 定期申報 — 5年自動轉註與免信託原因 100% RAG 合規檢核 */}
      <div className="bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-100 pb-3">
          <div className="text-sm font-extrabold text-slate-900">
            【真實公報實證】李○○副院長 114/11/01 定期申報（廉政專刊第309期 P.5-6）
          </div>
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300">
            <ShieldCheck className="w-4 h-4" />
            100% 通過 RAG 免信託適法性＆5年規則檢核（A類）
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* JAGUAR 滿 5 年自動轉註 */}
          <div className="rounded-xl border border-slate-200 p-4 bg-slate-50/70 space-y-2">
            <div className="text-xs font-bold text-sky-900">
              （四）汽車項目跨期5年檢核（`check_five_year_rule`）
            </div>
            <table className="w-full text-xs border-collapse bg-white rounded-lg overflow-hidden">
              <thead>
                <tr className="bg-slate-200 text-slate-700">
                  <th className="p-2 text-left">廠牌（汽缸）</th>
                  <th className="p-2 text-left">取得時間</th>
                  <th className="p-2 text-left">113/11/01 價額</th>
                  <th className="p-2 text-left">114/11/01 價額</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-slate-200">
                  <td className="p-2 font-bold">JAGUAR (1,997cc)</td>
                  <td className="p-2">109年05月19日</td>
                  <td className="p-2 text-slate-600">2,280,000</td>
                  <td className="p-2 font-extrabold text-emerald-700 bg-emerald-50">
                    (超過五年) ✅ 滿5年5個月自動轉註
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* 4類未能交付信託原因綠章 */}
          <div className="rounded-xl border border-emerald-200 p-4 bg-emerald-50/40 space-y-2">
            <div className="text-xs font-bold text-emerald-900">
              114年新增「未能交付信託原因」RAG 實質檢核結果：
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {[
                { label: '東京港區芝浦二丁目', tag: '國外土地／國外房屋' },
                { label: '雲林四湖鄉○○寮段', tag: '耕地，特定區域農牧用地' },
                { label: '大安區通化段○小段', tag: '自用房屋及坐落基地(單一戶)' },
                { label: '泰山區全興路/福興三街3筆', tag: '未登記建物(繼承)' },
              ].map((it) => (
                <div
                  key={it.label}
                  className="bg-white rounded-lg border border-emerald-200 px-3 py-2 flex items-center justify-between gap-2"
                >
                  <div>
                    <div className="font-bold text-slate-800">{it.label}</div>
                    <div className="text-emerald-700 font-medium">{it.tag}</div>
                  </div>
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 左右分屏：左側 B類紅鉛筆打勾 √ + 黃色長條便利貼 ｜ 右側 C類星號 ★ 欄位轉換傳真更正底稿 */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* 左屏：B類案件紅鉛筆逕修 (√) */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-slate-200 p-5 space-y-4 shadow-sm relative">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div>
              <span className="px-2.5 py-0.5 rounded bg-amber-100 text-amber-900 text-xs font-extrabold">
                情況 B：系統預設錯誤（承辦人逕予修改）
              </span>
              <h4 className="text-sm font-bold text-slate-900 mt-1">
                114年系統預設帶出「（房地總價額）」於繼承／單買土地案
              </h4>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 items-start">
            {/* 模擬申報表原件表格 */}
            <div className="flex-1 border-2 border-slate-800 rounded-lg overflow-hidden text-xs font-serif bg-[#fffdf9]">
              <div className="bg-slate-100 border-b border-slate-800 px-3 py-1.5 font-bold text-slate-900">
                （二）不動產 1. 土地（黃底審核範圍）
              </div>
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-slate-700 bg-yellow-100/70">
                    <th className="p-2 border-r border-slate-600 text-left">土地坐落</th>
                    <th className="p-2 border-r border-slate-600">取得時間/原因</th>
                    <th className="p-2 text-left">取得價額</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-400">
                    <td className="p-2 border-r border-slate-600">
                      嘉義縣梅山鄉○段0005地號（單買土地）
                    </td>
                    <td className="p-2 border-r border-slate-600 text-center">
                      111.3.8 / 買賣
                    </td>
                    <td className="p-2">
                      <div>2,097,150</div>
                      {showOverlay ? (
                        <span className="inline-flex items-center gap-1">
                          <span className="red-pencil-strike font-bold">（房地總價額）</span>
                          <span className="text-rose-600 font-extrabold text-base leading-none">
                            √
                          </span>
                        </span>
                      ) : (
                        <span>（房地總價額）</span>
                      )}
                    </td>
                  </tr>
                  <tr>
                    <td className="p-2 border-r border-slate-600">
                      高雄市路竹區○段0123地號（公同共有）
                    </td>
                    <td className="p-2 border-r border-slate-600 text-center">
                      112.10.10 / <span className="text-rose-700 font-bold">繼承</span>
                    </td>
                    <td className="p-2">
                      <div>897,150（公告現值）</div>
                      {showOverlay ? (
                        <span className="inline-flex items-center gap-1">
                          <span className="red-pencil-strike font-bold">（房地總價額）</span>
                          <span className="text-rose-600 font-extrabold text-base leading-none">
                            √
                          </span>
                        </span>
                      ) : (
                        <span>（房地總價額）</span>
                      )}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            {/* 右側黃色長條便利貼 */}
            {showOverlay && (
              <div className="sm:w-44 shrink-0 sticky-note-yellow rounded-r-xl p-3 text-xs text-amber-950 space-y-1.5">
                <div className="flex items-center gap-1 font-extrabold text-amber-900">
                  <StickyNote className="w-4 h-4" />
                  右側長條便利貼
                </div>
                <p className="leading-snug font-medium">
                  請第 5 組打字人員協助刪除紅筆打勾 <strong className="text-rose-700">√</strong>{' '}
                  處之系統預設「（房地總價額）」字句（繼承／單買土地不適用）。
                </p>
                <div className="pt-1 border-t border-amber-400/60 text-[12px] font-bold text-slate-700">
                  流程：承辦人 ➔ 組長 ➔ 登記桌 ➔ 第5組修改後銷毀
                </div>
              </div>
            )}
          </div>
        </div>

        {/* 右屏：C類案件傳真更正底稿（★ + 嚴禁網路更正禁令） */}
        <div className="lg:col-span-6 bg-white rounded-2xl border border-rose-200 p-5 space-y-4 shadow-sm">
          {/* 頂部紅字重要禁令 */}
          <div className="rounded-xl bg-rose-700 text-white px-4 py-2.5 flex items-center gap-2.5 shadow">
            <Ban className="w-5 h-5 shrink-0 text-amber-300" />
            <div className="text-xs font-bold leading-snug">
              【重要禁令】禁止建議申報人以網路更正！此舉易致誤刪資料、增加編製比對表負擔，一律以傳真／掃描簽章回傳辦理。
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <span className="px-2.5 py-0.5 rounded bg-rose-100 text-rose-900 text-xs font-extrabold">
                情況 C：需通知申報人更正（打星號 ★）
              </span>
              <h4 className="text-sm font-bold text-slate-900 mt-1">
                AI 一鍵將「附表一甲不動產」轉換為「附表四變動表」傳真更正底稿
              </h4>
            </div>
            <span className="inline-flex items-center gap-1 text-xs font-bold text-sky-800 bg-sky-50 px-2.5 py-1 rounded-lg border border-sky-200">
              <Printer className="w-3.5 h-3.5" />
              掛更正條碼分案
            </span>
          </div>

          <div className="border-2 border-slate-800 rounded-lg overflow-hidden text-xs font-serif bg-[#fffdf9]">
            <div className="bg-amber-100/80 border-b border-slate-800 px-3 py-1.5 font-bold text-slate-900 flex justify-between">
              <span>附表四：公職人員變動財產申報表（欄位自動轉換底稿）</span>
              <span className="text-rose-700">最左側打紅色星號 ★</span>
            </div>
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-slate-700 bg-slate-100">
                  <th className="p-2 border-r border-slate-600 w-10">標記</th>
                  <th className="p-2 border-r border-slate-600 text-left">土地坐落</th>
                  <th className="p-2 border-r border-slate-600 bg-yellow-200/80 text-rose-900">
                    變動時間
                    <span className="block text-[12px] font-normal text-slate-500">
                      (原:取得時間)
                    </span>
                  </th>
                  <th className="p-2 border-r border-slate-600 bg-yellow-200/80 text-rose-900">
                    變動原因
                    <span className="block text-[12px] font-normal text-slate-500">
                      (原:取得原因)
                    </span>
                  </th>
                  <th className="p-2 bg-yellow-200/80 text-rose-900 text-left">
                    變動時之價額
                    <span className="block text-[12px] font-normal text-slate-500">
                      (原:取得價額)
                    </span>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-slate-400">
                  <td className="p-2 border-r border-slate-600 text-center text-rose-600 text-base font-extrabold">
                    {showOverlay ? '★' : ''}
                  </td>
                  <td className="p-2 border-r border-slate-600">
                    桃園市龜山區大崗段0000地號
                  </td>
                  <td className="p-2 border-r border-slate-600 text-center font-bold">
                    113/11/06
                  </td>
                  <td className="p-2 border-r border-slate-600 text-center font-bold">買賣</td>
                  <td className="p-2 font-bold">17,300,000(房地總價額)</td>
                </tr>
                <tr>
                  <td className="p-2 border-r border-slate-600 text-center text-rose-600 text-base font-extrabold">
                    {showOverlay ? '★' : ''}
                  </td>
                  <td className="p-2 border-r border-slate-600">
                    新興段0005-2地號（母號0005分割出售）
                  </td>
                  <td className="p-2 border-r border-slate-600 text-center font-bold">
                    114/06/18
                  </td>
                  <td className="p-2 border-r border-slate-600 text-center font-bold">買賣出售</td>
                  <td className="p-2 font-bold">58,000,000</td>
                </tr>
              </tbody>
            </table>
          </div>

          <p className="text-xs text-slate-600">
            📌 <strong>裝訂鐵律：</strong>更正申報表回傳後，<strong>切勿</strong>與原始主表、附表裝訂在一起，僅置於同一卷夾一併移交第 5 組。
          </p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Activity, CheckCircle, AlertTriangle, RefreshCw } from "lucide-react";

export default function MonitoringLogsPage() {
  const [checks, setChecks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchChecks = async () => {
    try {
      setLoading(true);
      const data = await api.getMonitoringChecks();
      setChecks(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchChecks();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center border-b border-zinc-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Activity className="w-6 h-6 text-indigo-400" />
            Monitoring Check Logs & Health Audits
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Every background check cycle is recorded with HTTP status, duration, error isolation, and retry counters.
          </p>
        </div>
        <button
          onClick={fetchChecks}
          className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-700 rounded-lg text-xs font-medium"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Logs
        </button>
      </div>

      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-zinc-300">
          <thead className="bg-zinc-950 text-xs text-zinc-400 uppercase border-b border-zinc-800">
            <tr>
              <th className="py-3.5 px-4">Started At</th>
              <th className="py-3.5 px-4">Competitor</th>
              <th className="py-3.5 px-4">Status</th>
              <th className="py-3.5 px-4">HTTP Status</th>
              <th className="py-3.5 px-4">Duration</th>
              <th className="py-3.5 px-4">Found / New</th>
              <th className="py-3.5 px-4">Error Info</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60 font-mono text-xs">
            {checks.map((chk) => (
              <tr key={chk.id} className="hover:bg-zinc-800/30">
                <td className="py-3.5 px-4 text-zinc-400">
                  {new Date(chk.started_at).toLocaleTimeString()}
                </td>
                <td className="py-3.5 px-4 font-semibold text-white">
                  {chk.competitor_name || `Competitor #${chk.competitor_id}`}
                </td>
                <td className="py-3.5 px-4">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                    chk.success ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                  }`}>
                    {chk.success ? "✓ SUCCESS" : "✗ FAILED"}
                  </span>
                </td>
                <td className="py-3.5 px-4 text-zinc-300">
                  {chk.http_status || 200}
                </td>
                <td className="py-3.5 px-4 text-amber-300 font-bold">
                  {round(chk.duration_ms, 1)} ms
                </td>
                <td className="py-3.5 px-4 text-zinc-300">
                  {chk.articles_found} found / <strong className="text-emerald-400">{chk.new_articles_found} new</strong>
                </td>
                <td className="py-3.5 px-4 text-zinc-400 max-w-xs truncate">
                  {chk.error_message || "—"}
                </td>
              </tr>
            ))}
            {checks.length === 0 && !loading && (
              <tr>
                <td colSpan={7} className="text-center py-8 text-zinc-500">
                  No monitoring check logs recorded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function round(val: number, decimals: number) {
  return Number(Math.round(Number(val + "e" + decimals)) + "e-" + decimals);
}

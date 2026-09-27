"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { BarChart3, Clock, Layers, Zap } from "lucide-react";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [methodChart, setMethodChart] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([
      api.getAnalyticsOverview(),
      api.getMethodBreakdown()
    ]).then(([ov, methods]) => {
      setOverview(ov);
      setMethodChart(methods);
    }).catch(console.error);
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="border-b border-zinc-800 pb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-sky-400" />
          Monitoring History & Performance Analytics
        </h1>
        <p className="text-sm text-zinc-400 mt-1">
          Quantitative comparative analysis across RSS, XML Sitemap, and Direct Page detection strategies.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Average Detection Delay</span>
          <span className="text-2xl font-bold text-amber-300 font-mono mt-2 block">{overview?.average_detection_delay_display || "0 sec"}</span>
        </div>
        <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">5-Minute Target Compliance</span>
          <span className="text-2xl font-bold text-emerald-400 font-mono mt-2 block">{overview?.within_target_percentage ?? 0}%</span>
        </div>
        <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Isolated Errors</span>
          <span className="text-2xl font-bold text-zinc-300 font-mono mt-2 block">{overview?.failed_checks_count || 0}</span>
        </div>
      </div>

      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6">
        <h2 className="text-base font-bold text-white mb-4">Detection Strategy Efficiency (Avg Delay Seconds)</h2>
        {methodChart.length > 0 ? (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={methodChart}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="method" stroke="#71717a" fontSize={11} />
                <YAxis stroke="#71717a" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: "#18181b", borderColor: "#3f3f46", color: "#f4f4f5" }} />
                <Bar dataKey="avg_delay_seconds" fill="#38bdf8" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p className="text-zinc-500 text-sm text-center py-12">No method analytics recorded yet.</p>
        )}
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useSSE } from "@/hooks/useSSE";
import {
  Globe,
  Radio,
  FileText,
  Clock,
  Zap,
  AlertTriangle,
  CheckCircle,
  Plus,
  RefreshCw,
  TrendingUp,
  Layers,
  ArrowUpRight
} from "lucide-react";
import Link from "next/link";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from "recharts";

export default function DashboardPage() {
  const [overview, setOverview] = useState<any>(null);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [articles, setArticles] = useState<any[]>([]);
  const [delaysChart, setDelaysChart] = useState<any[]>([]);
  const [methodChart, setMethodChart] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadData = async () => {
    try {
      setRefreshing(true);
      const [ovData, compData, artData, delayData, methodData, notifData] = await Promise.all([
        api.getAnalyticsOverview(),
        api.getCompetitors(),
        api.getArticles({ limit: 10 }),
        api.getDetectionDelaysChart(),
        api.getMethodBreakdown(),
        api.getNotifications()
      ]);
      setOverview(ovData);
      setCompetitors(compData);
      setArticles(artData);
      setDelaysChart(delayData);
      setMethodChart(methodData);
      setNotifications(notifData);
    } catch (err) {
      console.error("Failed loading dashboard data:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Listen to live SSE events
  useSSE((evt) => {
    if (evt.event === "new_article") {
      loadData();
    }
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            Competitor Intelligence Command Center
            <span className="text-xs px-2.5 py-1 bg-sky-500/10 text-sky-400 border border-sky-500/20 rounded-full font-mono font-medium">
              Academic System v1.0
            </span>
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Continuous background monitoring, exact detection delay measurement, & multi-strategy extraction pipeline.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={refreshing}
            className="flex items-center gap-2 px-3.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 border border-zinc-700 rounded-lg text-sm font-medium transition"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin text-sky-400" : ""}`} />
            Refresh
          </button>
          <Link
            href="/competitors"
            className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-sky-600/20 transition"
          >
            <Plus className="w-4 h-4" />
            Add Competitor
          </Link>
        </div>
      </div>

      {/* KPI Cards Row */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-zinc-900 border border-zinc-800 rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
            <div className="flex items-center justify-between text-zinc-400 text-xs font-semibold uppercase tracking-wider">
              <span>Monitored Websites</span>
              <Globe className="w-4 h-4 text-sky-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-bold text-white">{overview?.active_competitors || 0}</span>
              <span className="text-xs text-zinc-400">{overview?.active_monitors || 0} Sources Active</span>
            </div>
          </div>

          <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
            <div className="flex items-center justify-between text-zinc-400 text-xs font-semibold uppercase tracking-wider">
              <span>Articles Detected</span>
              <FileText className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-bold text-white">{overview?.total_articles ?? 0}</span>
              <span className={`text-xs font-semibold ${overview?.within_target_percentage > 50 ? "text-emerald-400" : "text-amber-400"}`}>
                {overview?.within_target_percentage ?? 0}% Within 5m Target
              </span>
            </div>
          </div>

          <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
            <div className="flex items-center justify-between text-zinc-400 text-xs font-semibold uppercase tracking-wider">
              <span>Avg Detection Delay</span>
              <Clock className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-amber-300 font-mono">
                {overview?.average_detection_delay_display || "0 sec"}
              </span>
              <div className="text-xs text-zinc-400 mt-1 flex justify-between">
                <span>Fastest: <strong className="text-zinc-200">{overview?.fastest_delay_display}</strong></span>
                <span>Slowest: <strong className="text-zinc-200">{overview?.slowest_delay_display}</strong></span>
              </div>
            </div>
          </div>

          <div className="p-5 bg-zinc-900/70 border border-zinc-800 rounded-xl">
            <div className="flex items-center justify-between text-zinc-400 text-xs font-semibold uppercase tracking-wider">
              <span>System Health & Isolation</span>
              <Zap className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-3xl font-bold text-white">{overview?.total_checks || 0} Checks</span>
              <span className={`text-xs px-2 py-0.5 rounded font-semibold ${overview?.failed_checks_count === 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
                {overview?.failed_checks_count || 0} Errors Isolated
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Competitors Status & Latest Articles */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2/3): Competitor Health & Delay Chart */}
        <div className="lg:col-span-2 space-y-8">
          {/* Competitor Health Table */}
          <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Radio className="w-4 h-4 text-sky-400 animate-pulse" />
                  Competitor Monitoring Pipeline
                </h2>
                <p className="text-xs text-zinc-400">Continuous background polling status and active strategies.</p>
              </div>
              <Link href="/competitors" className="text-xs text-sky-400 hover:underline flex items-center gap-1">
                View All ({competitors.length}) <ArrowUpRight className="w-3 h-3" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-zinc-300">
                <thead className="bg-zinc-950 text-xs text-zinc-400 uppercase border-b border-zinc-800">
                  <tr>
                    <th className="py-3 px-4">Competitor</th>
                    <th className="py-3 px-4">Health</th>
                    <th className="py-3 px-4">Strategy</th>
                    <th className="py-3 px-4">Interval</th>
                    <th className="py-3 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-zinc-800/50">
                  {competitors.slice(0, 5).map((comp) => (
                    <tr key={comp.id} className="hover:bg-zinc-800/30">
                      <td className="py-3 px-4 font-medium text-white">
                        <Link href={`/competitors/${comp.id}`} className="hover:text-sky-400 transition">
                          {comp.name}
                        </Link>
                        <div className="text-xs text-zinc-500 font-mono truncate max-w-xs">{comp.website_url}</div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                          comp.health_status === "ONLINE"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : comp.health_status === "PAUSED"
                            ? "bg-zinc-500/10 text-zinc-400 border border-zinc-500/30"
                            : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
                        }`}>
                          <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${comp.health_status === "ONLINE" ? "bg-emerald-400" : "bg-amber-400"}`}></span>
                          {comp.health_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-xs text-zinc-400">
                        {comp.strategy_summary || "RSS + Sitemap"}
                      </td>
                      <td className="py-3 px-4 text-xs font-mono text-zinc-400">
                        {comp.monitoring_interval}s
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={async () => {
                            await api.checkCompetitorNow(comp.id);
                            loadData();
                          }}
                          className="px-2.5 py-1 bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-200 rounded border border-zinc-700"
                        >
                          Check Now
                        </button>
                      </td>
                    </tr>
                  ))}
                  {competitors.length === 0 && (
                    <tr>
                      <td colSpan={5} className="text-center py-6 text-zinc-500">
                        No competitors configured yet. Add your first competitor above.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Detection Delays Chart */}
          <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-base font-bold text-white mb-1 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-amber-400" />
              Real-Time Detection Delays (Seconds)
            </h2>
            <p className="text-xs text-zinc-400 mb-6">Calculated strictly from publication time to system detection time.</p>
            
            {delaysChart.length > 0 ? (
              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={delaysChart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="title" stroke="#71717a" fontSize={10} tickLine={false} />
                    <YAxis stroke="#71717a" fontSize={11} label={{ value: 'Seconds', angle: -90, position: 'insideLeft', fill: '#71717a' }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#18181b", borderColor: "#3f3f46", color: "#f4f4f5" }}
                      formatter={(val: any) => [`${val} sec`, "Detection Delay"]}
                    />
                    <Line type="monotone" dataKey="delay_seconds" stroke="#38bdf8" strokeWidth={2} dot={{ r: 4, fill: "#38bdf8" }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-48 flex items-center justify-center text-zinc-500 text-sm">
                No article delay records available yet.
              </div>
            )}
          </div>
        </div>

        {/* Right Column (1/3): Latest Articles Feed & Method Breakdown */}
        <div className="space-y-8">
          {/* Latest Detected Articles */}
          <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                Latest Articles
              </h2>
              <Link href="/articles" className="text-xs text-sky-400 hover:underline">
                View All
              </Link>
            </div>

            <div className="space-y-4">
              {articles.slice(0, 4).map((art) => (
                <div key={art.id} className="p-3.5 bg-zinc-950/60 border border-zinc-800/80 rounded-lg hover:border-zinc-700 transition">
                  <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
                    <span className="font-semibold text-sky-400">{art.competitor_name || "Competitor"}</span>
                    <span className="px-2 py-0.5 bg-zinc-800 rounded text-zinc-300 font-mono">{art.detection_method}</span>
                  </div>
                  <h3 className="font-medium text-white text-sm line-clamp-2 hover:text-sky-300 transition">
                    <Link href={`/articles#${art.id}`}>{art.title}</Link>
                  </h3>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="text-zinc-500 font-mono">
                      Delay: <strong className="text-amber-300">{art.detection_delay_display}</strong>
                    </span>
                    <span className={`px-2 py-0.5 rounded-full font-medium ${art.within_target ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"}`}>
                      {art.within_target ? "✓ Target" : "⚠ >5m Target"}
                    </span>
                  </div>
                </div>
              ))}
              {articles.length === 0 && (
                <p className="text-zinc-500 text-sm text-center py-6">No articles detected yet.</p>
              )}
            </div>
          </div>

          {/* Strategy Distribution */}
          <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-base font-bold text-white mb-1 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              Detection Method Breakdown
            </h2>
            <p className="text-xs text-zinc-400 mb-4">Volume of articles discovered per strategy.</p>
            {methodChart.length > 0 ? (
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={methodChart}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                    <XAxis dataKey="method" stroke="#71717a" fontSize={11} />
                    <YAxis stroke="#71717a" fontSize={11} />
                    <Tooltip contentStyle={{ backgroundColor: "#18181b", borderColor: "#3f3f46", color: "#f4f4f5" }} />
                    <Bar dataKey="article_count" fill="#818cf8" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="h-36 flex items-center justify-center text-zinc-500 text-sm">
                No strategy analytics recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

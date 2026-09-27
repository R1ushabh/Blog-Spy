"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Globe, Plus, Play, Pause, Trash2, Search, RefreshCw, CheckCircle, AlertCircle, Layers } from "lucide-react";
import Link from "next/link";

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  
  // Add Form State
  const [name, setName] = useState("");
  const [websiteUrl, setWebsiteUrl] = useState("");
  const [blogUrl, setBlogUrl] = useState("");
  const [feedUrl, setFeedUrl] = useState("");
  const [sitemapUrl, setSitemapUrl] = useState("");
  const [interval, setInterval] = useState(60);
  const [submitting, setSubmitting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const fetchCompetitors = async () => {
    try {
      setLoading(true);
      const data = await api.getCompetitors(search);
      setCompetitors(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompetitors();
  }, [search]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      const comp = await api.createCompetitor({
        name,
        website_url: websiteUrl,
        blog_url: blogUrl || undefined,
        feed_url: feedUrl || undefined,
        sitemap_url: sitemapUrl || undefined,
        monitoring_interval: Number(interval)
      });
      
      // Run analysis to show interactive analysis results card
      const analysis = await api.analyzeCompetitor(comp.id);
      setAnalysisResult(analysis);
      fetchCompetitors();
    } catch (err: any) {
      alert(err.message || "Failed to add competitor");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Globe className="w-6 h-6 text-sky-400" />
            Competitor Management & Automatic Analysis
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Add competitor targets. The system automatically discovers feeds, sitemaps, article patterns, and executes strategy selection.
          </p>
        </div>

        <button
          onClick={() => {
            setAnalysisResult(null);
            setShowAddModal(true);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-lg shadow-lg shadow-sky-600/20 transition"
        >
          <Plus className="w-4 h-4" />
          Add Competitor Target
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-4 bg-zinc-900/50 p-4 border border-zinc-800 rounded-xl">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search by competitor name or domain URL..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      {/* Competitors List Table */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-zinc-300">
          <thead className="bg-zinc-950 text-xs text-zinc-400 uppercase border-b border-zinc-800">
            <tr>
              <th className="py-3.5 px-4">Competitor</th>
              <th className="py-3.5 px-4">Health Status</th>
              <th className="py-3.5 px-4">Discovered Strategy</th>
              <th className="py-3.5 px-4">Interval</th>
              <th className="py-3.5 px-4">Last Checked</th>
              <th className="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {competitors.map((comp) => (
              <tr key={comp.id} className="hover:bg-zinc-800/30">
                <td className="py-4 px-4 font-medium text-white">
                  <Link href={`/competitors/${comp.id}`} className="hover:text-sky-400 font-semibold text-base block">
                    {comp.name}
                  </Link>
                  <span className="text-xs text-zinc-500 font-mono">{comp.website_url}</span>
                </td>
                <td className="py-4 px-4">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
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
                <td className="py-4 px-4 text-xs text-zinc-400 max-w-xs">
                  <div className="font-semibold text-zinc-200">{comp.strategy_summary || "RSS + Sitemap + Direct Page"}</div>
                  <div className="text-zinc-500 text-[11px] mt-0.5">Sources: {comp.sources?.length || 3} Discovered</div>
                </td>
                <td className="py-4 px-4 text-xs font-mono text-zinc-400">
                  {comp.monitoring_interval}s
                </td>
                <td className="py-4 px-4 text-xs text-zinc-400">
                  {comp.last_checked_at ? new Date(comp.last_checked_at).toLocaleTimeString() : "Never"}
                </td>
                <td className="py-4 px-4 text-right space-x-2">
                  <button
                    onClick={async () => {
                      await api.checkCompetitorNow(comp.id);
                      fetchCompetitors();
                    }}
                    className="px-2.5 py-1 bg-sky-950 hover:bg-sky-900 text-sky-300 text-xs font-medium rounded border border-sky-800"
                  >
                    Check Now
                  </button>
                  {comp.status === "PAUSED" ? (
                    <button
                      onClick={async () => {
                        await api.resumeCompetitor(comp.id);
                        fetchCompetitors();
                      }}
                      className="px-2 py-1 bg-emerald-950 hover:bg-emerald-900 text-emerald-300 text-xs rounded border border-emerald-800"
                      title="Resume Monitoring"
                    >
                      <Play className="w-3.5 h-3.5 inline" />
                    </button>
                  ) : (
                    <button
                      onClick={async () => {
                        await api.pauseCompetitor(comp.id);
                        fetchCompetitors();
                      }}
                      className="px-2 py-1 bg-amber-950 hover:bg-amber-900 text-amber-300 text-xs rounded border border-amber-800"
                      title="Pause Monitoring"
                    >
                      <Pause className="w-3.5 h-3.5 inline" />
                    </button>
                  )}
                  <button
                    onClick={async () => {
                      if (confirm(`Delete competitor ${comp.name}?`)) {
                        await api.deleteCompetitor(comp.id);
                        fetchCompetitors();
                      }
                    }}
                    className="px-2 py-1 bg-rose-950 hover:bg-rose-900 text-rose-300 text-xs rounded border border-rose-800"
                    title="Delete Competitor"
                  >
                    <Trash2 className="w-3.5 h-3.5 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {competitors.length === 0 && !loading && (
              <tr>
                <td colSpan={6} className="text-center py-8 text-zinc-500">
                  No competitor targets registered yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add Competitor Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-2">Add Competitor Website</h2>
            <p className="text-xs text-zinc-400 mb-6">
              Enter basic website details. The system will automatically investigate feeds, sitemaps, and structure.
            </p>

            {analysisResult ? (
              <div className="space-y-4">
                <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-emerald-400 text-sm flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 flex-shrink-0" />
                  <span>Automatic Website Investigation Complete!</span>
                </div>

                <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 space-y-3 text-xs">
                  <h3 className="font-bold text-white text-sm">Discovered Sources & Confidence:</h3>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="p-2 bg-zinc-900 rounded">
                      <span className="text-zinc-400 block">RSS / Atom Feeds:</span>
                      <strong className="text-sky-400">{analysisResult.rss_feeds?.length || 0} Found</strong>
                    </div>
                    <div className="p-2 bg-zinc-900 rounded">
                      <span className="text-zinc-400 block">XML Sitemaps:</span>
                      <strong className="text-emerald-400">{analysisResult.sitemaps?.length || 0} Found</strong>
                    </div>
                  </div>
                  <div>
                    <span className="text-zinc-400">Selected Strategy:</span>
                    <p className="text-zinc-200 font-semibold mt-0.5">{analysisResult.strategy_reason}</p>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setShowAddModal(false);
                    setAnalysisResult(null);
                  }}
                  className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-lg"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleCreate} className="space-y-4 text-sm">
                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Competitor Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Acme Corp Tech Blog"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white"
                  />
                </div>

                <div>
                  <label className="block text-zinc-300 font-medium mb-1">Main Website URL *</label>
                  <input
                    type="url"
                    required
                    placeholder="https://example.com"
                    value={websiteUrl}
                    onChange={(e) => setWebsiteUrl(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-xs"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-zinc-400 text-xs mb-1">Blog URL (Optional)</label>
                    <input
                      type="url"
                      placeholder="https://example.com/blog"
                      value={blogUrl}
                      onChange={(e) => setBlogUrl(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-zinc-400 text-xs mb-1">RSS Feed URL (Optional)</label>
                    <input
                      type="url"
                      placeholder="Auto-discovered if left blank"
                      value={feedUrl}
                      onChange={(e) => setFeedUrl(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-xs"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-zinc-400 text-xs mb-1">Monitoring Interval (Seconds)</label>
                  <input
                    type="number"
                    min="10"
                    max="3600"
                    value={interval}
                    onChange={(e) => setInterval(Number(e.target.value))}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-xs"
                  />
                </div>

                <div className="pt-4 flex justify-end gap-3 border-t border-zinc-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-zinc-800 text-zinc-300 rounded-lg text-sm"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-4 py-2 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-lg text-sm flex items-center gap-2"
                  >
                    {submitting && <RefreshCw className="w-4 h-4 animate-spin" />}
                    Analyze & Save Competitor
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

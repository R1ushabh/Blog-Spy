"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { FileText, Search, Clock, ExternalLink, Filter, CheckCircle, AlertTriangle, User, Tag } from "lucide-react";

export default function ArticlesPage() {
  const [articles, setArticles] = useState<any[]>([]);
  const [competitors, setCompetitors] = useState<any[]>([]);
  const [selectedComp, setSelectedComp] = useState<number | undefined>(undefined);
  const [selectedMethod, setSelectedMethod] = useState<string>("");
  const [search, setSearch] = useState("");
  const [targetFilter, setTargetFilter] = useState<string>("all");
  const [selectedArticle, setSelectedArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const withinT = targetFilter === "all" ? undefined : targetFilter === "true";
      const [artData, compData] = await Promise.all([
        api.getArticles({
          competitor_id: selectedComp,
          search: search || undefined,
          method: selectedMethod || undefined,
          within_target: withinT
        }),
        api.getCompetitors()
      ]);
      setArticles(artData);
      setCompetitors(compData);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [selectedComp, selectedMethod, search, targetFilter]);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <FileText className="w-6 h-6 text-emerald-400" />
          Detected Competitor Articles
        </h1>
        <p className="text-sm text-zinc-400 mt-1">
          Full content extraction, canonical deduplication, and exact delay measurement.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-4 bg-zinc-900/50 p-4 border border-zinc-800 rounded-xl">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 absolute left-3 top-3 text-zinc-500" />
          <input
            type="text"
            placeholder="Search title, author, or URL..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-9 pr-4 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-sky-500"
          />
        </div>

        <select
          value={selectedComp || ""}
          onChange={(e) => setSelectedComp(e.target.value ? Number(e.target.value) : undefined)}
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300"
        >
          <option value="">All Competitors</option>
          {competitors.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>

        <select
          value={selectedMethod}
          onChange={(e) => setSelectedMethod(e.target.value)}
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300"
        >
          <option value="">All Detection Methods</option>
          <option value="RSS">RSS</option>
          <option value="ATOM">ATOM</option>
          <option value="SITEMAP">SITEMAP</option>
          <option value="DIRECT_PAGE">DIRECT_PAGE</option>
        </select>

        <select
          value={targetFilter}
          onChange={(e) => setTargetFilter(e.target.value)}
          className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300"
        >
          <option value="all">All Target Statuses</option>
          <option value="true">Within 5-Min Target</option>
          <option value="false">Above 5-Min Target</option>
        </select>
      </div>

      {/* Articles Table */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl overflow-hidden">
        <table className="w-full text-left text-sm text-zinc-300">
          <thead className="bg-zinc-950 text-xs text-zinc-400 uppercase border-b border-zinc-800">
            <tr>
              <th className="py-3.5 px-4">Article Title</th>
              <th className="py-3.5 px-4">Competitor</th>
              <th className="py-3.5 px-4">Published</th>
              <th className="py-3.5 px-4">Detected</th>
              <th className="py-3.5 px-4">Exact Delay</th>
              <th className="py-3.5 px-4">Method</th>
              <th className="py-3.5 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/60">
            {articles.map((art) => (
              <tr key={art.id} className="hover:bg-zinc-800/30">
                <td className="py-4 px-4 font-medium text-white max-w-sm">
                  <button
                    onClick={() => setSelectedArticle(art)}
                    className="hover:text-sky-400 font-semibold text-sm text-left line-clamp-2"
                  >
                    {art.title}
                  </button>
                  <a
                    href={art.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-zinc-500 hover:text-zinc-400 font-mono flex items-center gap-1 mt-1 truncate"
                  >
                    {art.source_url} <ExternalLink className="w-3 h-3" />
                  </a>
                </td>
                <td className="py-4 px-4 font-medium text-sky-400 text-xs">
                  {art.competitor_name || "Competitor"}
                </td>
                <td className="py-4 px-4 text-xs font-mono text-zinc-400">
                  {art.publication_time ? new Date(art.publication_time).toLocaleTimeString() : "Unavailable"}
                </td>
                <td className="py-4 px-4 text-xs font-mono text-zinc-400">
                  {new Date(art.detected_at).toLocaleTimeString()}
                </td>
                <td className="py-4 px-4">
                  <div className="font-mono text-xs font-bold text-amber-300">
                    {art.detection_delay_display}
                  </div>
                  <span className={`inline-block text-[10px] px-1.5 py-0.2 rounded font-medium mt-0.5 ${
                    art.within_target ? "bg-emerald-500/10 text-emerald-400" : "bg-amber-500/10 text-amber-400"
                  }`}>
                    {art.within_target ? "✓ <= 5m" : "⚠ > 5m"}
                  </span>
                </td>
                <td className="py-4 px-4">
                  <span className="px-2 py-0.5 bg-zinc-800 rounded text-xs font-mono text-zinc-300">
                    {art.detection_method}
                  </span>
                </td>
                <td className="py-4 px-4 text-right">
                  <button
                    onClick={() => setSelectedArticle(art)}
                    className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-xs text-zinc-200 rounded border border-zinc-700"
                  >
                    View Article
                  </button>
                </td>
              </tr>
            ))}
            {articles.length === 0 && !loading && (
              <tr>
                <td colSpan={7} className="text-center py-8 text-zinc-500">
                  No articles found matching filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Article Detail Drawer Modal */}
      {selectedArticle && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-zinc-800 pb-4">
              <div>
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider">{selectedArticle.competitor_name}</span>
                <h2 className="text-xl font-bold text-white mt-1">{selectedArticle.title}</h2>
              </div>
              <button
                onClick={() => setSelectedArticle(null)}
                className="px-3 py-1 bg-zinc-800 text-zinc-400 hover:text-white rounded text-sm"
              >
                Close
              </button>
            </div>

            {/* Detection Timeline */}
            <div className="p-4 bg-zinc-950 border border-zinc-800 rounded-lg">
              <h3 className="text-xs font-semibold text-zinc-400 uppercase mb-3">Exact Detection Timeline</h3>
              <div className="grid grid-cols-4 gap-2 text-center text-xs">
                <div className="p-2 bg-zinc-900 rounded">
                  <span className="text-zinc-500 block">Published</span>
                  <strong className="text-zinc-200">{selectedArticle.publication_time ? new Date(selectedArticle.publication_time).toLocaleTimeString() : "N/A"}</strong>
                </div>
                <div className="p-2 bg-zinc-900 rounded">
                  <span className="text-zinc-500 block">Discovered</span>
                  <strong className="text-sky-400">{new Date(selectedArticle.detected_at).toLocaleTimeString()}</strong>
                </div>
                <div className="p-2 bg-zinc-900 rounded">
                  <span className="text-zinc-500 block">Calculated Delay</span>
                  <strong className="text-amber-300 font-mono">{selectedArticle.detection_delay_display}</strong>
                </div>
                <div className="p-2 bg-zinc-900 rounded">
                  <span className="text-zinc-500 block">5m Target</span>
                  <strong className={selectedArticle.within_target ? "text-emerald-400" : "text-amber-400"}>
                    {selectedArticle.within_target ? "✓ PASS" : "⚠ ABOVE TARGET"}
                  </strong>
                </div>
              </div>
            </div>

            {/* Metadata & Author */}
            <div className="grid grid-cols-2 gap-4 text-xs text-zinc-400 bg-zinc-900 p-3 rounded-lg border border-zinc-800">
              <div>
                <span>Author:</span> <strong className="text-zinc-200">{selectedArticle.author || "Unknown"}</strong>
              </div>
              <div>
                <span>Method:</span> <strong className="text-sky-400 font-mono">{selectedArticle.detection_method}</strong>
              </div>
              <div>
                <span>Canonical URL:</span> <span className="text-zinc-300 font-mono truncate block">{selectedArticle.canonical_url}</span>
              </div>
              <div>
                <span>Content Hash:</span> <span className="text-zinc-500 font-mono truncate block">{selectedArticle.content_hash}</span>
              </div>
            </div>

            {/* Extracted Body Preview */}
            <div className="space-y-2">
              <h3 className="text-xs font-semibold text-zinc-400 uppercase">Extracted Article Content</h3>
              <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800 text-sm text-zinc-300 max-h-60 overflow-y-auto leading-relaxed whitespace-pre-line">
                {selectedArticle.body || selectedArticle.excerpt || "No body content preview available."}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Cpu, Play, Square, Database, Trash2, RefreshCw, CheckCircle2, Zap, ShieldAlert } from "lucide-react";

export default function ScaleTestPage() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const data = await api.getScaleTestStatus();
      setStatus(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStatus();
    const timer = setInterval(fetchStatus, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-6 flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Cpu className="w-6 h-6 text-sky-400" />
            100-Website Scale Engine Control Center
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Reproducible high-concurrency load testing environment demonstrating async worker queues, per-domain rate limiting, and failure isolation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={async () => {
              setLoading(true);
              await api.seedScaleTest();
              await fetchStatus();
              setLoading(false);
            }}
            className="px-3.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-sky-400 border border-zinc-700 rounded-lg text-xs font-semibold flex items-center gap-2"
          >
            <Database className="w-3.5 h-3.5" /> Seed 100 Sites
          </button>
          
          {status?.is_running ? (
            <button
              onClick={async () => {
                await api.stopScaleTest();
                await fetchStatus();
              }}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold rounded-lg text-xs flex items-center gap-2"
            >
              <Square className="w-3.5 h-3.5 fill-current" /> Stop Test
            </button>
          ) : (
            <button
              onClick={async () => {
                await api.startScaleTest();
                await fetchStatus();
              }}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs flex items-center gap-2"
            >
              <Play className="w-3.5 h-3.5 fill-current" /> Start Scale Engine
            </button>
          )}

          <button
            onClick={async () => {
              if (confirm("Clear 100 scale test records?")) {
                await api.clearScaleTest();
                await fetchStatus();
              }
            }}
            className="px-3.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-rose-400 border border-zinc-800 rounded-lg text-xs"
          >
            <Trash2 className="w-3.5 h-3.5" /> Clear Data
          </button>
        </div>
      </div>

      {/* Real-Time Scale Metrics Panel */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-5 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Configured Targets</span>
          <span className="text-3xl font-bold text-white mt-2 block">{status?.total_competitors || 0}</span>
          <span className="text-xs text-sky-400 mt-1 block">100 Target Sites</span>
        </div>

        <div className="p-5 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Active Async Workers</span>
          <span className="text-3xl font-bold text-sky-400 mt-2 block">{status?.active_workers || 0}</span>
          <span className="text-xs text-zinc-400 mt-1 block">Max Concurrency Limit</span>
        </div>

        <div className="p-5 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Checks / Minute</span>
          <span className="text-3xl font-bold text-emerald-400 font-mono mt-2 block">{status?.checks_per_minute || 0}</span>
          <span className="text-xs text-zinc-400 mt-1 block">Throughput Rate</span>
        </div>

        <div className="p-5 bg-zinc-900/80 border border-zinc-800 rounded-xl">
          <span className="text-xs text-zinc-400 font-semibold uppercase tracking-wider block">Avg Check Duration</span>
          <span className="text-3xl font-bold text-amber-300 font-mono mt-2 block">{status?.average_check_duration_ms || 0} ms</span>
          <span className="text-xs text-zinc-400 mt-1 block">Avg Response Time</span>
        </div>
      </div>

      {/* Live Processing Pipeline Breakdown */}
      <div className="p-6 bg-zinc-900/70 border border-zinc-800 rounded-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Zap className="w-4 h-4 text-sky-400" />
          Live Concurrency Processing Breakdown
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-xs">
          <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800">
            <span className="text-zinc-400 block">Processing Now</span>
            <strong className="text-xl text-sky-400 font-mono">{status?.processing_count || 0}</strong>
          </div>
          <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800">
            <span className="text-zinc-400 block">Successful Checks</span>
            <strong className="text-xl text-emerald-400 font-mono">{status?.successful_checks || 0}</strong>
          </div>
          <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800">
            <span className="text-zinc-400 block">Retrying / Backoff</span>
            <strong className="text-xl text-amber-400 font-mono">{status?.retrying_checks || 0}</strong>
          </div>
          <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800">
            <span className="text-zinc-400 block">Articles Discovered</span>
            <strong className="text-xl text-indigo-400 font-mono">{status?.articles_detected || 0}</strong>
          </div>
        </div>
      </div>

      {/* Academic Architecture Answers & Explanation Section */}
      <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 space-y-6">
        <h2 className="text-lg font-bold text-white border-b border-zinc-800 pb-3 flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          100-Website Scalability Architecture Explanation
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm text-zinc-300">
          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">1. How are 100 websites scheduled?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              The continuous BackgroundScheduler uses non-blocking asyncio task queues to evaluate website check intervals. Jobs are enqueued into a Redis/Async worker pool without blocking the main event loop.
            </p>
          </div>

          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">2. Does one slow website block others?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              No. Every check task runs in an isolated asynchronous task worker with a strict 15-second request timeout (`httpx.AsyncClient(timeout=15)`). A slow target site yields control back to the worker pool immediately.
            </p>
          </div>

          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">3. How is concurrency handled?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Concurrency is bound by `asyncio.Semaphore(MAX_WORKERS)` (default 15 workers), ensuring CPU & network socket saturation are controlled preventing server overload.
            </p>
          </div>

          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">4. How are failures retried?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Temporary HTTP timeouts (5xx, 429) transition competitor health state from ONLINE -&gt; DEGRADED -&gt; OFFLINE. Retry attempts apply exponential backoff logging without halting the global worker queue.
            </p>
          </div>

          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">5. How is load controlled?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Domain throttling limits requests per competitor domain to max 1 concurrent connection, complying with web politeness and avoiding rate limits.
            </p>
          </div>

          <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800/80 space-y-2">
            <h3 className="font-bold text-sky-400">6. How are duplicate articles prevented at scale?</h3>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Canonical URL hashing combined with SHA-256 content fingerprints and DB indexed constraints ensures 0 repeated alerts even across 100 simultaneous targets.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

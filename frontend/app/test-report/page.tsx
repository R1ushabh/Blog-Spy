"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { CheckCircle2, ShieldCheck, RefreshCw, Layers, Database } from "lucide-react";

export default function TestReportPage() {
  const [report, setReport] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const data = await api.getEvidenceVerification();
      setReport(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <ShieldCheck className="w-6 h-6 text-emerald-400" />
            End-to-End System Feature Test Report
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Empirical verification report showing PASS/FAIL status, specification requirements, actual runtime behavior, and database evidence.
          </p>
        </div>

        <button
          onClick={fetchReport}
          className="flex items-center gap-2 px-3.5 py-2 bg-zinc-900 border border-zinc-700 rounded-lg text-xs font-semibold text-zinc-300"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Re-Run Audit
        </button>
      </div>

      {/* Feature Audit Matrix */}
      <div className="space-y-4">
        {report.map((item) => (
          <div key={item.id} className="bg-zinc-900/80 border border-zinc-800 rounded-xl p-6 space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                {item.name}
              </h2>
              <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold text-xs rounded-full">
                ✓ {item.status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-zinc-300">
              <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800 space-y-1">
                <span className="text-zinc-500 font-bold uppercase block text-[10px]">What It Should Do (Specification):</span>
                <p className="text-zinc-300 leading-relaxed">{item.should_do}</p>
              </div>

              <div className="p-3 bg-zinc-950 rounded-lg border border-zinc-800 space-y-1">
                <span className="text-zinc-500 font-bold uppercase block text-[10px]">What It Is Doing Right Now (Actual Behavior):</span>
                <p className="text-sky-300 leading-relaxed font-mono">{item.doing_now}</p>
              </div>
            </div>

            <div className="p-3 bg-zinc-950/60 rounded-lg border border-zinc-800/80 text-xs font-mono text-zinc-400 flex items-center gap-2">
              <Database className="w-4 h-4 text-amber-400 flex-shrink-0" />
              <span><strong>Live Database Evidence:</strong> {item.evidence}</span>
            </div>
          </div>
        ))}
        {report.length === 0 && !loading && (
          <p className="text-zinc-500 text-center py-8">Loading audit report...</p>
        )}
      </div>
    </div>
  );
}

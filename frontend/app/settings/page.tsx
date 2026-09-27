"use client";

import { useState } from "react";
import { Settings, Save } from "lucide-react";

export default function SettingsPage() {
  const [interval, setInterval] = useState(60);
  const [maxWorkers, setMaxWorkers] = useState(10);
  const [timeout, setTimeoutVal] = useState(15);
  const [userAgent, setUserAgent] = useState("CompetitorSpyBot/1.0 (+http://competitorspy.local/bot)");
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="border-b border-zinc-800 pb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-3">
          <Settings className="w-6 h-6 text-zinc-400" />
          System Settings & Crawler Configuration
        </h1>
        <p className="text-sm text-zinc-400 mt-1">
          Configure default monitoring parameters, worker concurrency limits, and email notification webhooks.
        </p>
      </div>

      <form onSubmit={handleSave} className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 space-y-6 text-sm">
        <div>
          <label className="block font-semibold text-zinc-200 mb-1">Default Monitoring Interval (Seconds)</label>
          <input
            type="number"
            min="10"
            max="3600"
            value={interval}
            onChange={(e) => setInterval(Number(e.target.value))}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-semibold text-zinc-200 mb-1">Max Async Workers</label>
            <input
              type="number"
              value={maxWorkers}
              onChange={(e) => setMaxWorkers(Number(e.target.value))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono"
            />
          </div>

          <div>
            <label className="block font-semibold text-zinc-200 mb-1">Request Timeout (Seconds)</label>
            <input
              type="number"
              value={timeout}
              onChange={(e) => setTimeoutVal(Number(e.target.value))}
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono"
            />
          </div>
        </div>

        <div>
          <label className="block font-semibold text-zinc-200 mb-1">Bot User-Agent Header</label>
          <input
            type="text"
            value={userAgent}
            onChange={(e) => setUserAgent(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-xs"
          />
        </div>

        <div className="pt-4 border-t border-zinc-800 flex items-center justify-between">
          {saved ? <span className="text-emerald-400 text-xs font-bold">✓ Settings Saved Successfully!</span> : <span />}
          <button
            type="submit"
            className="px-5 py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold rounded-lg text-sm flex items-center gap-2"
          >
            <Save className="w-4 h-4" /> Save Settings
          </button>
        </div>
      </form>
    </div>
  );
}

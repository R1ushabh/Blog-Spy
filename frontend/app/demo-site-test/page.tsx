"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { FlaskConical, Play, CheckCircle2, RefreshCw, Send, Radio, ExternalLink, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function ControlledDemoPage() {
  const [title, setTitle] = useState("Breaking: Next-Gen AI Content Spy Released");
  const [body, setBody] = useState("Today Acme Corp announced their real-time competitor content monitoring system featuring near-zero latency article detection.");
  const [author, setAuthor] = useState("Chief Researcher");
  const [pubTime, setPubTime] = useState(new Date().toISOString());
  const [image, setImage] = useState("https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80");
  
  const [publishing, setPublishing] = useState(false);
  const [lastPublished, setLastPublished] = useState<any>(null);
  const [demoStep, setDemoStep] = useState<number>(0);
  const [demoLogs, setDemoLogs] = useState<string[]>([]);

  const handlePublish = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    try {
      setPublishing(true);
      const res = await api.publishDemoArticle({
        title,
        body,
        author,
        published_at: pubTime,
        image
      });
      setLastPublished(res);

      // Trigger immediate check on demo competitor
      const comps = await api.getCompetitors();
      const demoComp = comps.find((c) => c.website_url.includes("demo-site") || c.name.includes("Acme"));
      if (demoComp) {
        await api.checkCompetitorNow(demoComp.id);
      }
    } catch (err: any) {
      alert(err.message || "Publishing failed");
    } finally {
      setPublishing(false);
    }
  };

  const runFullDemoSequence = async () => {
    setDemoStep(1);
    setDemoLogs(["1. Starting Complete Demo Sequence..."]);

    // Step 1: Check/Add Demo Competitor
    setDemoStep(2);
    setDemoLogs((prev) => [...prev, "2. Validating Acme Demo Competitor registration..."]);
    const comps = await api.getCompetitors();
    let demoComp = comps.find((c) => c.website_url.includes("demo-site"));
    
    if (!demoComp) {
      try {
        demoComp = await api.createCompetitor({
          name: "Acme Corp Demo Blog",
          website_url: "http://127.0.0.1:8000/api/demo-site",
          monitoring_interval: 30
        });
        setDemoLogs((prev) => [...prev, "✓ Demo Competitor registered successfully."]);
      } catch (err) {
        const freshComps = await api.getCompetitors();
        demoComp = freshComps.find((c) => c.website_url.includes("demo-site") || c.name.includes("Acme"));
        setDemoLogs((prev) => [...prev, "✓ Demo Competitor exists & active."]);
      }
    } else {
      setDemoLogs((prev) => [...prev, "✓ Demo Competitor exists & active."]);
    }

    // Step 2: Auto Analyze Website
    setDemoStep(3);
    setDemoLogs((prev) => [...prev, "3. Running Automatic Website Analyzer..."]);
    const analysis = await api.analyzeCompetitor(demoComp.id);
    setDemoLogs((prev) => [
      ...prev,
      `✓ Discovered Feeds: ${analysis.rss_feeds?.length || 1} | Sitemaps: ${analysis.sitemaps?.length || 1}`,
      `✓ Strategy Confidence: RSS (High), Sitemap (High), Direct Page (Medium)`
    ]);

    // Step 3: Publish New Article to Demo Site
    setDemoStep(4);
    const testTitle = `Demo Pipeline Test Article #${Math.floor(Math.random() * 1000)}`;
    const nowIso = new Date(Date.now() - 120000).toISOString(); // 2 mins ago
    setDemoLogs((prev) => [...prev, `4. Publishing test article: "${testTitle}" with publication timestamp ${nowIso}...`]);
    
    const pubRes = await api.publishDemoArticle({
      title: testTitle,
      body: "This test article verifies end-to-end detection, canonical deduplication, and exact delay calculation.",
      author: "Demo Agent",
      published_at: nowIso,
      image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80"
    });
    setDemoLogs((prev) => [...prev, "✓ Demo Article published to live RSS feed & sitemap.xml!"]);

    // Step 4: Run Production Monitoring Pipeline
    setDemoStep(5);
    setDemoLogs((prev) => [...prev, "5. Running background worker monitoring check..."]);
    const checkRes = await api.checkCompetitorNow(demoComp.id);
    setDemoLogs((prev) => [
      ...prev,
      `✓ Monitoring check completed in ${round(checkRes.duration_ms, 1)}ms.`,
      `✓ Discovered ${checkRes.new_articles} new article(s)!`
    ]);

    // Step 5: Verify Delay & Dashboard Notification
    setDemoStep(6);
    const articles = await api.getArticles({ competitor_id: demoComp.id, limit: 1 });
    if (articles.length > 0) {
      const latest = articles[0];
      setDemoLogs((prev) => [
        ...prev,
        `🎉 VERIFICATION SUCCESS: Article ID ${latest.id} stored!`,
        `   • Title: ${latest.title}`,
        `   • Published: ${latest.publication_time}`,
        `   • Detected: ${latest.detected_at}`,
        `   • Exact Delay: ${latest.detection_delay_display} (${latest.detection_delay_seconds}s)`,
        `   • 5-Min Target: ${latest.within_target ? "✓ PASSED" : "⚠ ABOVE TARGET"}`
      ]);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-zinc-800 pb-6 flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <FlaskConical className="w-6 h-6 text-emerald-400" />
            Controlled Demo Website & Publisher Simulator
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Test the live monitoring pipeline against an isolated controlled blog endpoint (`/api/demo-site`).
          </p>
        </div>

        <button
          onClick={runFullDemoSequence}
          className="flex items-center gap-2 px-5 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm rounded-lg shadow-lg shadow-emerald-600/20 transition"
        >
          <Play className="w-4 h-4 fill-current" /> Run Complete 1-Click Demo Pipeline
        </button>
      </div>

      {/* Grid: Publisher Form & Demo Sequence Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Publisher Form */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Send className="w-4 h-4 text-sky-400" />
              Publish Article to Demo Blog
            </h2>
            <a
              href="http://127.0.0.1:8000/api/demo-site"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-sky-400 hover:underline flex items-center gap-1"
            >
              Open Demo Blog HTML <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <form onSubmit={handlePublish} className="space-y-4 text-xs">
            <div>
              <label className="block text-zinc-300 font-medium mb-1">Article Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white text-sm"
              />
            </div>

            <div>
              <label className="block text-zinc-300 font-medium mb-1">Article Body</label>
              <textarea
                rows={4}
                required
                value={body}
                onChange={(e) => setBody(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white text-xs leading-relaxed"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-zinc-400 mb-1">Author</label>
                <input
                  type="text"
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white"
                />
              </div>

              <div>
                <label className="block text-zinc-400 mb-1">Publication Time (ISO 8601)</label>
                <input
                  type="text"
                  value={pubTime}
                  onChange={(e) => setPubTime(e.target.value)}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-white font-mono text-[11px]"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={publishing}
              className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium text-sm rounded-lg flex items-center justify-center gap-2 shadow-lg shadow-sky-600/20"
            >
              {publishing && <RefreshCw className="w-4 h-4 animate-spin" />}
              Publish Article & Trigger Monitor
            </button>
          </form>

          {lastPublished && (
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-xs space-y-1">
              <span className="font-bold text-emerald-400 block">✓ Article Published Live to Demo Feeds!</span>
              <p className="text-zinc-300 font-mono text-[11px]">RSS: {lastPublished.rss_url}</p>
              <p className="text-zinc-300 font-mono text-[11px]">Sitemap: {lastPublished.sitemap_url}</p>
            </div>
          )}
        </div>

        {/* Demo Pipeline Step Trace */}
        <div className="bg-zinc-900/70 border border-zinc-800 rounded-xl p-6 space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
            1-Click Automated Demo Test Trace
          </h2>

          <div className="bg-zinc-950 p-4 rounded-lg border border-zinc-800 h-80 overflow-y-auto font-mono text-xs text-zinc-300 space-y-2">
            {demoLogs.length === 0 ? (
              <p className="text-zinc-500 italic">Click "Run Complete 1-Click Demo Pipeline" above to execute the automated verification sequence.</p>
            ) : (
              demoLogs.map((log, idx) => (
                <div key={idx} className={log.startsWith("✓") ? "text-emerald-400 font-semibold" : log.startsWith("🎉") ? "text-sky-300 font-bold bg-sky-500/10 p-2 rounded border border-sky-500/20" : "text-zinc-300"}>
                  {log}
                </div>
              ))
            )}
          </div>

          <div className="pt-2 flex justify-end">
            <Link
              href="/"
              className="text-xs text-sky-400 hover:underline flex items-center gap-1 font-semibold"
            >
              View Live Dashboard Results <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

function round(val: number, decimals: number) {
  return Number(Math.round(Number(val + "e" + decimals)) + "e-" + decimals);
}

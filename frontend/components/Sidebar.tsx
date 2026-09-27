"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Globe,
  FileText,
  Activity,
  BarChart3,
  Cpu,
  FlaskConical,
  CheckCircle2,
  Settings,
  Radio
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/competitors", label: "Competitors", icon: Globe },
  { href: "/articles", label: "Detected Articles", icon: FileText },
  { href: "/monitoring", label: "Monitoring Logs", icon: Activity },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/scale-test", label: "100-Site Scale Test", icon: Cpu },
  { href: "/demo-site-test", label: "Controlled Demo Site", icon: FlaskConical },
  { href: "/test-report", label: "Audit Test Report", icon: CheckCircle2 },
  { href: "/evidence", label: "Evidence & Audit", icon: CheckCircle2 },
  { href: "/settings", label: "System Settings", icon: Settings },
];

export function Sidebar({ sseConnected }: { sseConnected?: boolean }) {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-zinc-800 bg-zinc-950 flex flex-col justify-between h-screen sticky top-0">
      <div>
        <div className="p-5 border-b border-zinc-800 flex items-center space-x-3">
          <div className="p-2 bg-sky-500/10 border border-sky-500/30 rounded-lg text-sky-400">
            <Radio className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <h1 className="font-bold text-white text-base leading-tight">BlogSpy AI</h1>
            <p className="text-xs text-zinc-400">Real-Time Competitor Radar</p>
          </div>
        </div>

        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-zinc-800 text-sky-400 border border-zinc-700/50"
                    : "text-zinc-400 hover:text-white hover:bg-zinc-900"
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? "text-sky-400" : "text-zinc-500"}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-400">Engine Stream</span>
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
            sseConnected ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/10 text-amber-400 border border-amber-500/30"
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${sseConnected ? "bg-emerald-400 animate-ping" : "bg-amber-400"}`}></span>
            {sseConnected ? "LIVE SSE" : "POLLING"}
          </span>
        </div>
      </div>
    </aside>
  );
}

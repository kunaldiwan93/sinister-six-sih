"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Network,
  Users,
  Clock,
  ArrowLeftRight,
  PhoneCall,
  AlertTriangle,
  Bot,
  Database,
  Activity,
  Settings,
  ShieldCheck,
} from "lucide-react";

const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Network Explorer", href: "/explorer", icon: Network },
  { label: "Entities Directory", href: "/entities", icon: Users },
  { label: "Investigation Timeline", href: "/timeline", icon: Clock },
  { label: "Transactions", href: "/transactions", icon: ArrowLeftRight },
  { label: "Communications", href: "/communications", icon: PhoneCall },
  { label: "Alerts & Anomalies", href: "/alerts", icon: AlertTriangle },
  { label: "AI Assistant", href: "/assistant", icon: Bot },
  { label: "Data Sources", href: "/sources", icon: Database },
  { label: "Analysis Runs", href: "/analysis", icon: Activity },
  { label: "Settings & Ethics", href: "/settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 shrink-0 bg-surface border-r border-border flex flex-col h-screen sticky top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-5 border-b border-border/80 bg-surface">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-nexus-500 to-indigo-700 flex items-center justify-center shadow-glow">
          <ShieldCheck className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-mono font-bold tracking-widest text-sm text-white">NEXUS</span>
            <span className="px-1.5 py-0.2 rounded bg-nexus-950 border border-nexus-800 text-[10px] font-mono text-nexus-400">INTEL</span>
          </div>
          <p className="text-[10px] text-slate-400 font-mono tracking-tight">AI Investigation Platform</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 pb-2 text-[10px] font-mono uppercase tracking-wider text-slate-400">
          Core Modules
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-xs font-medium transition-colors ${
                isActive
                  ? "bg-nexus-900/40 text-nexus-300 border border-nexus-600/40 shadow-sm"
                  : "text-slate-400 hover:text-slate-200 hover:bg-surface-raised"
              }`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-nexus-400" : "text-slate-500"}`} />
              <span className="truncate">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Security Statement Footer */}
      <div className="p-3.5 border-t border-border/70 bg-surface-raised/30">
        <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span>Local Engine Active</span>
        </div>
        <p className="text-[10px] text-slate-400 mt-1 leading-tight">
          Investigative Lead Assistant v1.0
        </p>
      </div>
    </aside>
  );
}

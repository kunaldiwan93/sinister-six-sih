import React from "react";
import { LucideIcon } from "lucide-react";

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: string;
  variant?: "default" | "danger" | "warning" | "success" | "info";
  onClick?: () => void;
}

export function KpiCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  variant = "default",
  onClick,
}: KpiCardProps) {
  let border = "border-border hover:border-nexus-500/50";
  let iconBg = "bg-nexus-950 text-nexus-400 border-nexus-800/60";

  if (variant === "danger") {
    border = "border-red-900/50 hover:border-red-500/60 bg-gradient-to-b from-red-950/20 to-surface";
    iconBg = "bg-red-950 text-red-400 border-red-800/60";
  } else if (variant === "warning") {
    border = "border-amber-900/50 hover:border-amber-500/60 bg-gradient-to-b from-amber-950/20 to-surface";
    iconBg = "bg-amber-950 text-amber-400 border-amber-800/60";
  } else if (variant === "success") {
    border = "border-emerald-900/50 hover:border-emerald-500/60";
    iconBg = "bg-emerald-950 text-emerald-400 border-emerald-800/60";
  }

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg bg-surface border ${border} transition-all duration-200 ${
        onClick ? "cursor-pointer hover:bg-surface-raised" : ""
      }`}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
          {title}
        </span>
        <div className={`p-2 rounded-md border ${iconBg}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">
          {value}
        </span>
        {trend && (
          <span className="text-xs font-mono text-nexus-400">{trend}</span>
        )}
      </div>
      {subtitle && (
        <p className="mt-1 text-xs text-slate-400 truncate">{subtitle}</p>
      )}
    </div>
  );
}

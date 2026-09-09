import React from "react";
import { RiskLevel } from "@/types";

interface RiskBadgeProps {
  level: RiskLevel | string;
  score?: number;
  className?: string;
}

export function RiskBadge({ level, score, className = "" }: RiskBadgeProps) {
  const normalizedLevel = (level || "LOW").toUpperCase();

  let bg = "bg-emerald-950/80 border-emerald-700/60 text-emerald-400";
  let dot = "bg-emerald-400";

  if (normalizedLevel === "CRITICAL") {
    bg = "bg-red-950/90 border-red-600/70 text-red-300 shadow-[0_0_12px_rgba(239,68,68,0.25)]";
    dot = "bg-red-500 animate-pulse";
  } else if (normalizedLevel === "HIGH") {
    bg = "bg-orange-950/80 border-orange-600/60 text-orange-300";
    dot = "bg-orange-400";
  } else if (normalizedLevel === "MODERATE" || normalizedLevel === "MEDIUM") {
    bg = "bg-amber-950/80 border-amber-600/60 text-amber-300";
    dot = "bg-amber-400";
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium border ${bg} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`} />
      <span>{normalizedLevel}</span>
      {score !== undefined && (
        <span className="opacity-75 border-l border-white/10 pl-1 ml-0.5">
          {score.toFixed(0)}/100
        </span>
      )}
    </span>
  );
}

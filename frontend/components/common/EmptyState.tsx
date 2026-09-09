import React from "react";
import { Inbox } from "lucide-react";

interface EmptyStateProps {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({
  title = "No Data Found",
  description = "No records match the active criteria or filter parameters.",
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="w-full rounded-lg border border-dashed border-border/60 bg-surface/50 p-10 flex flex-col items-center justify-center text-center">
      <div className="p-3 rounded-full bg-slate-900 border border-slate-800 text-slate-400 mb-3">
        <Inbox className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-slate-200">{title}</h3>
      <p className="mt-1 text-xs text-slate-400 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-4 px-3 py-1.5 rounded bg-nexus-600 hover:bg-nexus-500 text-xs font-medium text-white transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}

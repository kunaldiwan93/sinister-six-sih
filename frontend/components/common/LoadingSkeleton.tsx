import React from "react";
import { AlertTriangle, Inbox, RefreshCw } from "lucide-react";

export function LoadingSkeleton({ className = "h-32", text = "Loading intelligence data..." }: { className?: string; text?: string }) {
  return (
    <div className={`w-full rounded-lg bg-surface border border-border/50 p-6 flex flex-col items-center justify-center animate-pulse ${className}`}>
      <RefreshCw className="w-6 h-6 text-nexus-400 animate-spin mb-3 opacity-80" />
      <span className="text-xs font-mono text-slate-400">{text}</span>
    </div>
  );
}

export function EmptyState({
  title = "No Data Found",
  description = "No records match the active criteria or filter parameters.",
  actionLabel,
  onAction,
}: {
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
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

export function ErrorState({
  message = "Failed to load requested intelligence data.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="w-full rounded-lg border border-red-900/50 bg-red-950/20 p-6 flex flex-col items-center justify-center text-center">
      <div className="p-3 rounded-full bg-red-950 border border-red-800 text-red-400 mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-red-200">System Error</h3>
      <p className="mt-1 text-xs text-red-300 max-w-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 px-3 py-1.5 rounded bg-red-900/60 hover:bg-red-800 border border-red-700/60 text-xs font-medium text-red-100 transition-colors"
        >
          Retry Request
        </button>
      )}
    </div>
  );
}
